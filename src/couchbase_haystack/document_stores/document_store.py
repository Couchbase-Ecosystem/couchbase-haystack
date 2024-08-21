# SPDX-FileCopyrightText: 2023-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0
import logging
import re
from datetime import timedelta
from typing import Any, Dict, List, Optional, Union

from couchbase import search
from couchbase.cluster import Cluster
from couchbase.collection import Collection
from couchbase.exceptions import DocumentExistsException

# needed for options -- cluster, timeout, SQL++ (N1QL) query, etc.
from couchbase.options import SearchOptions
from couchbase.result import MultiMutationResult, SearchResult
from couchbase.scope import Scope
from couchbase.search import SearchQuery
from couchbase.vector_search import VectorQuery, VectorSearch
from haystack import default_from_dict, default_to_dict
from haystack.core.serialization import generate_qualified_class_name
from haystack.dataclasses.document import Document
from haystack.document_stores.errors import DocumentStoreError, DuplicateDocumentError
from haystack.document_stores.types import DuplicatePolicy
from haystack.utils.auth import Secret, deserialize_secrets_inplace

from .auth import CouchbaseCertificateAuthenticator, CouchbasePasswordAuthenticator
from .cluster_options import CouchbaseClusterOptions
from .filters import _normalize_filters

logger = logging.getLogger(__name__)


class CouchbaseDocumentStore:
    """
    CouchbaseDocumentStore is a DocumentStore implementation that uses
    [Couchbase capella](https://cloud.couchbase.com) service that is easy to deploy, operate, and scale.
    """

    def __init__(
        self,
        *,
        cluster_connection_string: Secret = Secret.from_env_var("CB_CONNECTION_STRING"),
        authenticator: Union[CouchbasePasswordAuthenticator, CouchbaseCertificateAuthenticator],
        cluster_options: CouchbaseClusterOptions = CouchbaseClusterOptions(),
        bucket: str,
        scope: str,
        collection: str,
        vector_search_index: str,
        **kwargs: Dict[str, Any],
    ):
        """
        Creates a new CouchbaseDocumentStore instance.


        :raises ValueError: If the collection name contains invalid characters.
        """
        if collection and not bool(re.match(r"^[a-zA-Z0-9\-_]+$", collection)):
            msg = f'Invalid collection name: "{collection}". It can only contain letters, numbers, -, or _.'
            raise ValueError(msg)

        self.cluster_connection_string = cluster_connection_string
        self.authenticator = authenticator
        self.cluster_options = cluster_options
        self.bucket = bucket
        self.scope_name = scope
        self.collection_name = collection
        self.vector_search_index = vector_search_index
        self._connection: Optional[Cluster] = None
        self._scope: Optional[Scope] = None
        self._collection: Optional[Collection] = None
        self._kwargs = kwargs

    @property
    def connection(self) -> Cluster:
        if self._connection is None:
            cluster_options = self.cluster_options.get_cluster_options(self.authenticator.get_cb_auth())
            if self.cluster_options.get("profile") is not None:
                cluster_options.apply_profile(self.cluster_options["profile"])
            self._connection = Cluster(
                self.cluster_connection_string.resolve_value(),
                cluster_options,
                **self._kwargs,
            )
            self._connection.wait_until_ready(timeout=timedelta(seconds=60))
        return self._connection

    @property
    def scope(self) -> Scope:
        if self._scope is None:
            bucket = self.connection.bucket(self.bucket)
            scopes_specs = bucket.collections().get_all_scopes()
            scope_found = False
            collection_found = False
            for scope_spec in scopes_specs:
                if scope_spec.name == self.scope_name:
                    scope_found = True
                    for col_spec in scope_spec.collections:
                        if col_spec.name == self.collection_name:
                            collection_found = True
            if not scope_found:
                msg = f"Scope '{self.scope_name}' does not exist in bucket '{self.bucket}'."
                raise ValueError(msg)
            if not collection_found:
                msg = f"Collection '{self.collection_name}' does not exist in scope '{self.scope_name}'."
                raise ValueError(msg)
            self._scope = self.connection.bucket(self.bucket).scope(self.scope_name)
        return self._scope

    @property
    def collection(self) -> Collection:
        if self._collection is None:
            self._collection = self.scope.collection(self.collection_name)
        return self._collection

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes the component to a dictionary.

        :returns:
            Dictionary with serialized data.
        """
        return default_to_dict(
            self,
            cluster_connection_string=self.cluster_connection_string.to_dict(),
            authenticator=self.authenticator.to_dict(),
            cluster_options=self.cluster_options.to_dict(),
            bucket=self.bucket,
            scope=self.scope_name,
            collection=self.collection_name,
            vector_search_index=self.vector_search_index,
            **self._kwargs,
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CouchbaseDocumentStore":
        """
        Deserializes the component from a dictionary.

        :param data:
            Dictionary to deserialize from.
        :returns:
              Deserialized component.
        """
        if data["init_parameters"]["authenticator"]["type"] == generate_qualified_class_name(CouchbasePasswordAuthenticator):
            data["init_parameters"]["authenticator"] = CouchbasePasswordAuthenticator.from_dict(
                data["init_parameters"]["authenticator"]
            )
        else:
            data["init_parameters"]["authenticator"] = CouchbaseCertificateAuthenticator.from_dict(
                data["init_parameters"]["authenticator"]
            )
        data["init_parameters"]["cluster_options"] = CouchbaseClusterOptions.from_dict(data["init_parameters"]["cluster_options"])
        deserialize_secrets_inplace(data["init_parameters"], keys=["cluster_connection_string"])
        return default_from_dict(cls, data)

    def count_documents(self) -> int:
        """
        Returns how many documents are present in the document store.

        :returns: The number of documents in the document store.
        """
        return self.scope.search_indexes().get_indexed_documents_count(self.vector_search_index)

    def filter_documents(self, filters: Optional[Dict[str, Any]] = None) -> List[Document]:
        """
        Returns the documents that match the filters provided.

        For a detailed specification of the filters,
        refer to the Haystack [documentation](https://docs.haystack.deepset.ai/v2.0/docs/metadata-filtering).

        :param filters: The filters to apply. It returns only the documents that match the filters.
        :returns: A list of Documents that match the given filters.
        """
        search_filters: SearchQuery
        # sort:str
        if filters:
            search_filters = _normalize_filters(filters)
        else:
            search_filters = search.MatchAllQuery()
        logger.debug(search_filters.encodable)
        request = search.SearchRequest(search_filters)
        options = SearchOptions(fields=["*"], limit=10000)
        response = self.scope.search(self.vector_search_index, request, options)
        return self.__get_doc_from_kv(response)

    def write_documents(self, documents: List[Document], policy: DuplicatePolicy = DuplicatePolicy.NONE) -> int:
        """
        Writes documents into the couchbase collection.

        :param documents: A list of Documents to write to the document store.
        :param policy: The duplicate policy to use when writing documents.
        :raises DuplicateDocumentError: If a document with the same ID already exists in the document store
             and the policy is set to DuplicatePolicy.FAIL (or not specified).
        :raises ValueError: If the documents are not of type Document.
        :returns: The number of documents written to the document store.
        """

        if len(documents) > 0:
            if not isinstance(documents[0], Document):
                msg = "param 'documents' must contain a list of objects of type Document"
                raise ValueError(msg)

        if policy == DuplicatePolicy.NONE:
            policy = DuplicatePolicy.FAIL

        cb_documents = []
        for doc in documents:
            doc_dict = doc.to_dict(flatten=False)
            doc_dict = {k: v for k, v in doc_dict.items() if v is not None}
            if "sparse_embedding" in doc_dict:
                sparse_embedding = doc_dict.pop("sparse_embedding", None)
                if sparse_embedding:
                    logger.warning(
                        "Document %s has the `sparse_embedding` field set,"
                        "but storing sparse embeddings in Couchbase is not currently supported."
                        "The `sparse_embedding` field will be ignored.",
                        doc.id,
                    )
            cb_documents.append(doc_dict)
        written_docs = len(documents)

        operations = {doc["id"]: doc for doc in cb_documents}
        try:
            result: MultiMutationResult
            if policy == DuplicatePolicy.FAIL:
                result = self.collection.insert_multi(operations)
            else:
                result = self.collection.upsert_multi(operations)
        except Exception as e:
            logger.error("write error", e)
            msg = f"Failed to write documents to Couchbase. Error: {e}"
            raise DocumentStoreError(msg) from e
        if not result.all_ok and result.exceptions:
            duplicate_ids = []
            other_errors = []
            for id, ex in result.exceptions.items():
                if isinstance(ex, DocumentExistsException):
                    duplicate_ids.append(id)
                else:
                    other_errors.append({"id": id, "exception": ex})
            if len(duplicate_ids) > 0:
                msg = f"IDs '{', '.join(duplicate_ids)}' already exist in the document store."
                raise DuplicateDocumentError(msg)
            if len(other_errors) > 0:
                msg = f"Failed to write documents to couchbase. Errors:\n{other_errors}"
                raise DocumentStoreError(msg)
        logger.debug("date written")
        return written_docs

    def delete_documents(self, document_ids: List[str]) -> None:
        """
        Deletes all documents with a matching document_ids from the document store.

        :param document_ids: the document ids to delete
        """
        if not document_ids:
            return
        self.collection.remove_multi(keys=document_ids)

    def _embedding_retrieval(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        search_query: SearchQuery = None,
        limit: Optional[int] = None,
    ) -> List[Document]:
        """
        Find the documents that are most similar to the provided `query_embedding` by using a vector similarity metric.

        :param query_embedding: Embedding of the query
        :param top_k: How many documents to be returned by the vector query.
        :param search: Search filters param which is parsed to the Couchbase search query. The vector query and
        search query are ORed operation.
        :param limit: Maximum number of Documents to be return by the couchbase fts search request. Default value is top_k.
        :returns: A list of Documents that are most similar to the given `query_embedding`
        :raises ValueError: If `query_embedding` is empty.
        :raises Document StoreError: If the retrieval of documents from Couchbase  fails.
        """
        if not query_embedding:
            msg = "Query embedding must not be empty"
            raise ValueError(msg)

        vector_search = VectorSearch.from_vector_query(
            VectorQuery(field_name="embedding", vector=query_embedding, num_candidates=top_k)
        )
        request = search.SearchRequest.create(vector_search)
        if search_query:
            request.with_search_query(search_query)

        if limit is None:
            limit = top_k
        options = SearchOptions(fields=["*"], limit=limit)
        response = self.scope.search(self.vector_search_index, request, options)
        return self.__get_doc_from_kv(response)

    def __get_doc_from_kv(self, response: SearchResult) -> List[Document]:
        documents: List[Document] = []
        ids: List[str] = []
        scores: List[float] = []
        for doc in response.rows():
            ids.append(doc.id)
            scores.append(doc.score)
        kv_response = self.collection.get_multi(keys=ids)
        if not kv_response.all_ok and kv_response.exceptions:
            errors = []
            for id, ex in kv_response.exceptions.items():
                errors.append({"id": id, "exception": ex})
            if len(errors) > 0:
                msg = f"Failed to write documents to couchbase. Errors:\n{errors}"
                raise DocumentStoreError(msg)
        for i, id in enumerate(ids):
            get_result = kv_response.results.get(id)
            if get_result is not None and get_result.success:
                value = get_result.value
                value["id"] = id
                value["score"] = scores[i]
            documents.append(Document.from_dict(value))
        return documents
