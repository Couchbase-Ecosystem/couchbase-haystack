# SPDX-FileCopyrightText: 2023-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0
import logging
import re
from dataclasses import dataclass
from datetime import timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from couchbase import search
from couchbase.bucket import Bucket
from couchbase.cluster import Cluster
from couchbase.collection import Collection
from couchbase.exceptions import DocumentExistsException
from couchbase.n1ql import QueryScanConsistency

# needed for options -- cluster, timeout, SQL++ (N1QL) query, etc.
from couchbase.options import QueryOptions, SearchOptions
from couchbase.result import MultiMutationResult, QueryResult, SearchResult
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
from .search_filters import _normalize_filters
from .sql_filters import normalize_sql_filters

logger = logging.getLogger(__name__)


class QueryVectorSearchType(str, Enum):
    """Enum for search types supported by Couchbase GSI."""

    ANN = "ANN"
    KNN = "KNN"


class QueryVectorSearchSimilarity(str, Enum):
    """Enum for similarity metrics supported by Couchbase GSI."""

    COSINE = "COSINE"
    DOT = "DOT"
    L2 = "L2"
    EUCLIDEAN = "EUCLIDEAN"
    L2_SQUARED = "L2_SQUARED"
    EUCLIDEAN_SQUARED = "EUCLIDEAN_SQUARED"


@dataclass
class CouchbaseQueryOptions:
    """Dataclass for storing query options specifically for Couchbase SQL++ (N1QL) queries.

    Args:
        timeout: The timeout duration for the query. Defaults to 60 seconds.
        scan_consistency: The scan consistency level for the query. See `couchbase.n1ql.QueryScanConsistency`.
                          Defaults to None, which implies Couchbase's default behavior.
    """

    timeout: timedelta = timedelta(seconds=60)
    scan_consistency: Optional[Union[QueryScanConsistency, str]] = None

    __cb_query_options: Optional[QueryOptions] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the CouchbaseQueryOptions object to a dictionary.

        Returns:
            A dictionary representation of the object.
        """
        return default_to_dict(
            self,
            timeout=self.timeout.total_seconds(),
            scan_consistency=(
                self.scan_consistency.value if isinstance(self.scan_consistency, QueryScanConsistency) else self.scan_consistency
            ),
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CouchbaseQueryOptions":
        """Deserializes a dictionary into a CouchbaseQueryOptions object.

        Args:
            data: The dictionary to deserialize from.

        Returns:
            A CouchbaseQueryOptions instance.
        """
        init_parameters = data.get("init_parameters", {})
        init_parameters["scan_consistency"] = (
            QueryScanConsistency(init_parameters["scan_consistency"]) if init_parameters.get("scan_consistency") else None
        )
        init_parameters["timeout"] = timedelta(seconds=init_parameters.get("timeout")) if init_parameters.get("timeout") else None
        return default_from_dict(cls, data)

    def cb_query_options(self) -> QueryOptions:
        """Returns the underlying Couchbase SDK `QueryOptions` object.

        Returns:
            The configured `couchbase.options.QueryOptions` instance.
        """
        return QueryOptions(
            timeout=self.timeout.total_seconds(),
            scan_consistency=(
                self.scan_consistency.value if isinstance(self.scan_consistency, QueryScanConsistency) else self.scan_consistency
            ),
        )


class CouchbaseDocumentStore:
    """Base class for Couchbase document stores that provides common functionality
    for managing connections, scopes, collections, and basic document operations.
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
        **kwargs: Dict[str, Any],
    ):
        """Creates a new CouchbaseDocumentStore instance.

        Args:
            cluster_connection_string: Connection string for the Couchbase cluster
            authenticator: Authentication method (password or certificate based)
            cluster_options: Options for configuring the cluster connection
            bucket: Name of the Couchbase bucket to use
            scope: Name of the scope within the bucket
            collection: Name of the collection within the scope
            kwargs: Additional keyword arguments passed to the Cluster constructor

        Raises:
            ValueError: If the provided collection name contains invalid characters.
        """
        if collection and not bool(re.match(r"^[a-zA-Z0-9\-_]+$", collection)):
            msg = f'Invalid collection name: "{collection}". It can only contain letters, numbers, -, or _.'
            raise ValueError(msg)

        self.cluster_connection_string = cluster_connection_string
        self.authenticator = authenticator
        self.cluster_options = cluster_options
        self.bucket_name = bucket
        self.scope_name = scope
        self.collection_name = collection
        self._connection: Optional[Cluster] = None
        self._bucket: Optional[Bucket] = None
        self._scope: Optional[Scope] = None
        self._collection: Optional[Collection] = None
        self._kwargs = kwargs

    @property
    def connection(self) -> Cluster:
        """Establishes and returns the Couchbase Cluster connection.

        Initializes the connection if it doesn't exist, applying cluster options and authentication.
        Waits until the cluster is ready before returning.

        Returns:
            The active `couchbase.cluster.Cluster` instance.

        Raises:
            DocumentStoreError: If the connection cannot be established or times out.
        """
        if self._connection is None:
            try:
                cluster_options = self.cluster_options.get_cluster_options(self.authenticator.get_cb_auth())
                if self.cluster_options.get("profile") is not None:
                    cluster_options.apply_profile(self.cluster_options["profile"])
                self._connection = Cluster(
                    self.cluster_connection_string.resolve_value(),
                    cluster_options,
                    **self._kwargs,
                )
                self._connection.wait_until_ready(timeout=timedelta(seconds=60))
            except TimeoutError as e:
                msg = f"Failed to establish connection: {e}"
                raise DocumentStoreError(msg) from e
            except Exception as e:
                msg = f"Failed to establish connection: {e}"
                raise DocumentStoreError(msg) from e
        return self._connection

    @property
    def bucket(self) -> Bucket:
        """Returns the Couchbase `Bucket` object associated with this document store.

        Returns:
            The `couchbase.bucket.Bucket` instance.

        Raises:
            Exceptions from the underlying `connection.bucket()` call if the bucket doesn't exist or is inaccessible.
        """
        if self._bucket is None:
            self._bucket = self.connection.bucket(self.bucket_name)
        return self._bucket

    @property
    def scope(self) -> Scope:
        """Returns the Couchbase `Scope` object associated with this document store.

        Returns:
            The `couchbase.scope.Scope` instance.

        Raises:
            ValueError: If the specified scope or collection does not exist in the bucket.
        """
        if self._scope is None:
            scopes_specs = self.bucket.collections().get_all_scopes()
            scope_found = False
            collection_found = False
            for scope_spec in scopes_specs:
                if scope_spec.name == self.scope_name:
                    scope_found = True
                    for col_spec in scope_spec.collections:
                        if col_spec.name == self.collection_name:
                            collection_found = True
            if not scope_found:
                msg = f"Scope '{self.scope_name}' does not exist in bucket '{self.bucket_name}'."
                raise ValueError(msg)
            if not collection_found:
                msg = f"Collection '{self.collection_name}' does not exist in scope '{self.scope_name}'."
                raise ValueError(msg)
            self._scope = self.bucket.scope(self.scope_name)
        return self._scope

    @property
    def collection(self) -> Collection:
        """Returns the Couchbase `Collection` object associated with this document store.

        Returns:
            The `couchbase.collection.Collection` instance.

        Raises:
            Exceptions from the underlying `scope.collection()` call if the collection is inaccessible.
        """
        if self._collection is None:
            self._collection = self.scope.collection(self.collection_name)
        return self._collection

    def _base_to_dict(self) -> Dict[str, Any]:
        """Creates a base dictionary containing common configuration parameters for serialization.

        This is intended to be used by subclasses in their `to_dict` methods.

        Returns:
            A dictionary with core configuration details.
        """
        return {
            "cluster_connection_string": self.cluster_connection_string.to_dict(),
            "authenticator": self.authenticator.to_dict(),
            "cluster_options": self.cluster_options.to_dict(),
            "bucket": self.bucket_name,
            "scope": self.scope_name,
            "collection": self.collection_name,
            **self._kwargs,
        }

    def write_documents(self, documents: List[Document], policy: DuplicatePolicy = DuplicatePolicy.NONE) -> int:
        """Writes documents into the couchbase collection.

        Args:
            documents: A list of Documents to write to the document store.
            policy: The duplicate policy to use when writing documents.
                    `FAIL`: (Default if `NONE`) Raise an error if a document ID already exists.
                    `OVERWRITE`: Replace existing documents with the same ID.

        Raises:
            DuplicateDocumentError: If `policy` is `FAIL` and a document with the same ID already exists.
            ValueError: If `documents` is not a list of `Document` objects.
            DocumentStoreError: If any other error occurs during the write operation.

        Returns:
            The number of documents successfully written to the document store.
        """
        if len(documents) == 0:
            return 0

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
            logger.error(f"write error {e}")
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
        logger.debug("data written")
        return written_docs

    def delete_documents(self, document_ids: List[str]) -> None:
        """Deletes all documents with a matching document_ids from the document store.

        Args:
            document_ids: the document ids to delete
        """
        if not document_ids:
            return
        self.collection.remove_multi(keys=document_ids)


class CouchbaseSearchDocumentStore(CouchbaseDocumentStore):
    """CouchbaseSearchDocumentStore is a DocumentStore implementation that uses
    [Couchbase capella](https://cloud.couchbase.com) service that is easy to deploy, operate, and scale.

    The document store supports both scope-level and global-level vector search indexes:

    - Scope-level indexes (default): The vector search index is created at the scope level and only searches
      documents within that scope
    - Global-level indexes: The vector search index is created at the bucket level and can search across all
      scopes and collections in the bucket

    The index level is specified using the `is_global_level_index` parameter during initialization.
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
        is_global_level_index: bool = False,
        **kwargs: Dict[str, Any],
    ):
        """Creates a new CouchbaseSearchDocumentStore instance.

        Args:
            cluster_connection_string: Connection string for the Couchbase cluster
            authenticator: Authentication method (password or certificate based)
            cluster_options: Options for configuring the cluster connection
            bucket: Name of the Couchbase bucket to use
            scope: Name of the scope within the bucket
            collection: Name of the collection within the scope
            vector_search_index: Name of the FTS index (which must include vector indexing) to use for searches.
            is_global_level_index: If `True`, use a global (bucket-level) FTS index.
                                  If `False` (default), use a scope-level FTS index.
            kwargs: Additional keyword arguments passed to the Cluster constructor.
        """
        super().__init__(
            cluster_connection_string=cluster_connection_string,
            authenticator=authenticator,
            cluster_options=cluster_options,
            bucket=bucket,
            scope=scope,
            collection=collection,
            **kwargs,
        )
        self.vector_search_index = vector_search_index
        self.is_global_level_index = is_global_level_index

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the component to a dictionary.

        Returns:
            Dictionary with serialized data.
        """
        return default_to_dict(
            self,
            **self._base_to_dict(),
            vector_search_index=self.vector_search_index,
            is_global_level_index=self.is_global_level_index,
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CouchbaseSearchDocumentStore":
        """Deserializes the component from a dictionary.

        Args:
            data: Dictionary to deserialize from.

        Returns:
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

    def _get_search_interface(self):
        """Returns the appropriate Couchbase search interface based on the `is_global_level_index` configuration.

        Returns:
            The Couchbase search index manager object.
        """
        if not self.is_global_level_index:
            return self.scope.search_indexes()
        return self.connection.search_indexes()

    def count_documents(self) -> int:
        """Returns how many documents are present in the document store.

        Returns:
            The number of documents in the document store.
        """
        search_interface = self._get_search_interface()
        return search_interface.get_indexed_documents_count(self.vector_search_index)

    def filter_documents(self, filters: Optional[Dict[str, Any]] = None) -> List[Document]:
        """Returns the documents that match the filters provided.

        For a detailed specification of the filters,
        refer to the Haystack [documentation](https://docs.haystack.deepset.ai/v2.0/docs/metadata-filtering).

        Args:
            filters: The filters to apply. It returns only the documents that match the filters.

        Returns:
            A list of Documents that match the given filters.

        Raises:
            DocumentStoreError: If the search request fails.
        """
        search_filters: SearchQuery
        if filters:
            search_filters = _normalize_filters(filters)
        else:
            search_filters = search.MatchAllQuery()
        logger.debug(search_filters.encodable)
        request = search.SearchRequest(search_filters)
        options = SearchOptions(fields=["*"], limit=10000)

        if not self.is_global_level_index:
            response = self.scope.search(self.vector_search_index, request, options)
        else:
            response = self.connection.search(self.vector_search_index, request, options)

        return self.__get_doc_from_kv(response)

    def _embedding_retrieval(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        search_query: SearchQuery = None,
        limit: Optional[int] = None,
    ) -> List[Document]:
        """Find the documents that are most similar to the provided `query_embedding` by using a vector similarity metric.

        Args:
            query_embedding: Embedding of the query
            top_k: How many documents to be returned by the vector query
            filters: Optional dictionary of filters to apply before the vector search.
                     Refer to Haystack documentation for filter structure (https://docs.haystack.deepset.ai/v2.0/docs/metadata-filtering).
            search_query: Search filters param which is parsed to the Couchbase search query. The vector query and
                          search query are ORed operation.
            limit: Maximum number of Documents to return. Defaults to top_k if not specified.

        Returns:
            A list of Documents that are most similar to the given `query_embedding`

        Raises:
            ValueError: If `query_embedding` is empty
            DocumentStoreError: If the retrieval of documents from Couchbase fails
        """
        if not query_embedding:
            msg = "Query embedding must not be empty"
            raise ValueError(msg)
        pre_filter: Optional[SearchQuery] = None
        if filters is not None:
            pre_filter = _normalize_filters(filters)
            logger.debug(f"pre_filter.encodable: {pre_filter.encodable}")

        vector_search = VectorSearch.from_vector_query(
            VectorQuery(field_name="embedding", vector=query_embedding, num_candidates=top_k, prefilter=pre_filter)
        )
        request = search.SearchRequest.create(vector_search)
        if search_query:
            request.with_search_query(search_query)

        if limit is None:
            limit = top_k
        options = SearchOptions(fields=["*"], limit=limit)

        if not self.is_global_level_index:
            response = self.scope.search(self.vector_search_index, request, options)
        else:
            response = self.connection.search(self.vector_search_index, request, options)

        return self.__get_doc_from_kv(response)

    def __get_doc_from_kv(self, response: SearchResult) -> List[Document]:
        """Fetches the full document content from Couchbase KV storage based on IDs from a SearchResult.

        This helper method takes the results of an FTS/Vector search (which might only contain IDs and scores)
        and retrieves the complete documents using a multi-get operation for efficiency.

        Args:
            response: The `SearchResult` object containing document IDs and scores.

        Returns:
            A list of Haystack `Document` objects, populated with content and scores.

        Raises:
            DocumentStoreError: If fetching documents from KV fails for any ID.
        """
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


class CouchbaseQueryDocumentStore(CouchbaseDocumentStore):
    """CouchbaseQueryDocumentStore is a DocumentStore implementation that uses
    Couchbase Global Secondary Index (GSI) for vector search capabilities.

    This document store supports two types of vector indexes:

    - BHIVE Index: A dedicated vector index for high-performance ANN vector search
    - Composite Secondary Index: Includes vectors alongside other fields for combined filtering

    Both index types support various vector similarity metrics and can be configured
    with additional parameters for optimizing vector search performance.
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
        search_type: QueryVectorSearchType,
        similarity: Union[QueryVectorSearchSimilarity, str],
        nprobes: Optional[int] = None,
        query_options: CouchbaseQueryOptions = CouchbaseQueryOptions(
            timeout=timedelta(seconds=60), scan_consistency=QueryScanConsistency.NOT_BOUNDED
        ),
        **kwargs: Dict[str, Any],
    ):
        """Creates a new CouchbaseGSIDocumentStore instance.

        Args:
            cluster_connection_string: Connection string for the Couchbase cluster
            authenticator: Authentication method (password or certificate based)
            cluster_options: Options for configuring the cluster connection
            bucket: Name of the Couchbase bucket to use
            scope: Name of the scope within the bucket
            collection: Name of the collection within the scope
            search_type: Type of vector search (ANN or KNN).
            similarity: Similarity metric to use (COSINE, DOT, L2 or EUCLIDEAN, L2_SQUARED or EUCLIDEAN_SQUARED) or
            string representation of the enum.
            nprobes: Number of probes for the ANN search.
                Defaults to None, uses the value set at index creation time.
            query_options: Options controlling SQL++ query execution (timeout, scan consistency).
            kwargs: Additional keyword arguments passed to the `CouchbaseDocumentStore` base class constructor.
        """
        super().__init__(
            cluster_connection_string=cluster_connection_string,
            authenticator=authenticator,
            cluster_options=cluster_options,
            bucket=bucket,
            scope=scope,
            collection=collection,
            **kwargs,
        )
        self.search_type = QueryVectorSearchType(search_type) if isinstance(search_type, str) else search_type
        self.similarity: str = (
            similarity.upper()
            if isinstance(similarity, str)
            else (similarity.value if isinstance(similarity, QueryVectorSearchSimilarity) else None)
        )
        if self.similarity is None:
            err_msg = f"Invalid similarity metric: {similarity}"
            raise ValueError(err_msg)
        self.nprobes = nprobes
        self.query_options = query_options

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the component to a dictionary.

        Returns:
            Dictionary with serialized data.
        """
        return default_to_dict(
            self,
            **self._base_to_dict(),  # cluster details
            query_options=self.query_options.to_dict() if self.query_options else None,
            search_type=self.search_type.value if isinstance(self.search_type, QueryVectorSearchType) else self.search_type,
            similarity=self.similarity,
            nprobes=self.nprobes,
            **self._kwargs,
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CouchbaseQueryDocumentStore":
        """Deserializes the component from a dictionary.

        Args:
            data: Dictionary to deserialize from.

        Returns:
            Deserialized component.
        """
        init_params = data.get("init_parameters", {})

        # Handle authenticator deserialization
        if init_params["authenticator"]["type"] == generate_qualified_class_name(CouchbasePasswordAuthenticator):
            init_params["authenticator"] = CouchbasePasswordAuthenticator.from_dict(init_params["authenticator"])
        else:
            init_params["authenticator"] = CouchbaseCertificateAuthenticator.from_dict(init_params["authenticator"])

        # Handle cluster options deserialization
        init_params["cluster_options"] = CouchbaseClusterOptions.from_dict(init_params["cluster_options"])

        if init_params["query_options"]:
            init_params["query_options"] = CouchbaseQueryOptions.from_dict(init_params["query_options"])

        # Handle secrets
        deserialize_secrets_inplace(init_params, keys=["cluster_connection_string"])

        return default_from_dict(cls, data)

    def count_documents(self) -> int:
        """Returns how many documents are present in the document store.

        Returns:
            The number of documents in the document store.
        """
        query = f"SELECT COUNT(*) as count FROM `{self.collection_name}`"  # noqa: S608
        result = self.scope.query(query, self.query_options.cb_query_options()).execute()
        return result[0]["count"]

    def filter_documents(self, filters: Optional[Dict[str, Any]] = None) -> List[Document]:
        """Returns the documents that match the filters provided.

        For a detailed specification of the filters,
        refer to the Haystack [documentation](https://docs.haystack.deepset.ai/v2.0/docs/metadata-filtering).

        Args:
            filters: The filters to apply using SQL++ WHERE clause syntax.
                    Refer to the Haystack documentation for filter structure.

        Returns:
            A list of Documents that match the given filters.

        Raises:
            DocumentStoreError: If the SQL++ query execution fails.
        """
        query_str = f"SELECT d.*, meta().id as id FROM `{self.collection_name}` as d"  # noqa: S608
        where_clause = ""

        if filters:
            normalized_filters = normalize_sql_filters(filters)
            where_clause = f" WHERE {normalized_filters}"
            query_str += where_clause
        try:
            result = self.scope.query(query_str, self.query_options.cb_query_options())
            documents = []

            for row in result.rows():
                # Convert row to Document
                doc_dict = row.copy()
                documents.append(Document.from_dict(doc_dict))

            return documents

        except Exception as e:
            msg = f"Failed to filter documents: {e}"
            logger.error(msg)
            raise DocumentStoreError(msg) from e

    def _embedding_retrieval(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        nprobes: Optional[int] = None,
    ) -> List[Document]:
        """Find the documents that are most similar to the provided `query_embedding` by using a vector similarity metric.

        Args:
            query_embedding: Embedding of the query
            top_k: How many documents to retrieve based on vector similarity.
            filters: Optional dictionary of filters to apply using a SQL++ WHERE clause before the vector search.
            nprobes: Number of probes for the ANN search. If None, uses the value set at index creation time
            or the value set at the document store level.

        Returns:
            A list of Documents most similar to the `query_embedding`, potentially pre-filtered.

        Raises:
            ValueError: If `query_embedding` is empty.
            DocumentStoreError: If the SQL++ query execution fails.
        """
        if not query_embedding:
            msg = "Query embedding must not be empty"
            raise ValueError(msg)

        # Construct the SQL++ query with vector search
        query_context = f"`{self.bucket_name}`.`{self.scope_name}`.`{self.collection_name}`"

        # Convert embedding to string representation for query
        query_vector_str = str(query_embedding)

        # Handle filters if provided
        where_clause = ""
        if filters:
            normalized_filters = normalize_sql_filters(filters)
            where_clause = f"WHERE {normalized_filters}"

        if nprobes is None:
            nprobes = self.nprobes
        # Determine the appropriate distance function based on search type
        if self.search_type == QueryVectorSearchType.ANN:
            nprobes_exp = f", {nprobes}" if nprobes else ""
            distance_function_exp = f"APPROX_VECTOR_DISTANCE(d.embedding, {query_vector_str}, '{self.similarity}'{nprobes_exp})"
        else:
            distance_function_exp = f"VECTOR_DISTANCE(d.embedding, {query_vector_str}, '{self.similarity}')"

        # Build the query
        query_str = f"""
        SELECT d.*, meta().id as id, {distance_function_exp} as score
        FROM {query_context} d
        {where_clause}
        ORDER BY score
        LIMIT {top_k}
        """  # noqa: S608  # query_vector_str is a float array, where_clause is normalized by normalize_sql_filters

        try:

            query_options = self.query_options.cb_query_options()
            # Execute the query
            result: QueryResult = self.connection.query(
                query_str,
                query_options,
            )

            # Process results
            documents = []
            for row in result.rows():
                # Convert row to Document
                doc_dict = row.copy()
                documents.append(Document.from_dict(doc_dict))

            return documents

        except Exception as e:
            msg = f"Failed to retrieve documents with vector search: {e}"
            logger.error(msg)
            raise DocumentStoreError(msg) from e

    # def normalize_score(self, score: float) -> float:
    #     """
    #     Normalizes the raw vector search score based on the similarity metric.

    #     For l2_distance, the normalized score is the reciprocal of the distance (1 / distance).
    #     For cosine and dot_product, the raw score is already the similarity score and is returned as-is.

    #     Args:
    #         score: The raw score or distance returned by the vector search.
    #         similarity: The similarity metric used ("l2_distance", "cosine", or "dot_product").

    #     Returns:
    #         The normalized score.
    #     """
    #     if self.similarity in {"L2", "EUCLIDEAN", "L2_SQUARED", "EUCLIDEAN_SQUARED"}:
    #         return 1.0 / score if score != 0 else float("inf")
    #     else:
    #         return score
