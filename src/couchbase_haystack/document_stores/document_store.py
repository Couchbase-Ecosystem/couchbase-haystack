# SPDX-FileCopyrightText: 2023-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0
import logging
import re
from datetime import timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field

from couchbase import search
from couchbase.cluster import Cluster
from couchbase.collection import Collection
from couchbase.exceptions import DocumentExistsException

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


class VectorSimilarityMetric(str, Enum):
    """Enum for vector similarity metrics supported by Couchbase GSI."""

    L2 = "L2"
    EUCLIDEAN = "EUCLIDEAN"
    L2_SQUARED = "L2_SQUARED"
    EUCLIDEAN_SQUARED = "EUCLIDEAN_SQUARED"
    COSINE = "COSINE"
    DOT = "DOT"


class IndexType(str, Enum):
    """Enum for index types supported by Couchbase GSI."""

    BHIVE = "BHIVE"
    COMPOSITE = "COMPOSITE"


@dataclass
class IndexParams:
    """
    Configuration parameters for Couchbase GSI vector index.
    
    This class consolidates all parameters related to vector index configuration into a single object.
    """
    dimension: int = 768
    similarity: VectorSimilarityMetric = VectorSimilarityMetric.L2
    description: Optional[str] = None
    include_fields: Optional[List[str]] = None
    kwargs: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize default values and validate parameters"""
        if self.dimension <= 0:
            raise ValueError("dimension must be greater than 0")
            
        if self.include_fields is None:
            self.include_fields = []
            
        # Default description for composite index if not provided
        if self.description is None and self.similarity in [VectorSimilarityMetric.L2, VectorSimilarityMetric.EUCLIDEAN]:
            self.description = "SQ8"
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert parameters to dictionary for serialization and index creation"""
        result = {
            "dimension": self.dimension,
            "similarity": VectorSimilarityMetric[self.similarity].value,
            "description": self.description,
            "include_fields": self.include_fields,
            **self.kwargs,
        }
        
        if self.description:
            result["description"] = self.description
            
        return result
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IndexParams":
        """Create parameters from dictionary"""
        # Handle similarity conversion from string if needed
        if isinstance(data.get("similarity"), str):
            data["similarity"] = VectorSimilarityMetric(data["similarity"])
            
        return cls(**data)


class CouchbaseDocumentStore:
    """
    Base class for Couchbase document stores that provides common functionality
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
        """
        Creates a new CouchbaseDocumentStore instance.

        :param cluster_connection_string: Connection string for the Couchbase cluster
        :param authenticator: Authentication method (password or certificate based)
        :param cluster_options: Options for configuring the cluster connection
        :param bucket: Name of the Couchbase bucket to use
        :param scope: Name of the scope within the bucket
        :param collection: Name of the collection within the scope
        :param kwargs: Additional keyword arguments passed to the Cluster constructor
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
        self._connection: Optional[Cluster] = None
        self._scope: Optional[Scope] = None
        self._collection: Optional[Collection] = None
        self._kwargs = kwargs

    @property
    def connection(self) -> Cluster:
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
            self._scope = bucket.scope(self.scope_name)
        return self._scope

    @property
    def collection(self) -> Collection:
        if self._collection is None:
            self._collection = self.scope.collection(self.collection_name)
        return self._collection

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
            logger.error("write error {e}")
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
        """
        Deletes all documents with a matching document_ids from the document store.

        :param document_ids: the document ids to delete
        """
        if not document_ids:
            return
        self.collection.remove_multi(keys=document_ids)


class CouchbaseSearchDocumentStore(CouchbaseDocumentStore):
    """
    CouchbaseSearchDocumentStore is a DocumentStore implementation that uses
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
        """
        Creates a new CouchbaseSearchDocumentStore instance.

        :param cluster_connection_string: Connection string for the Couchbase cluster
        :param authenticator: Authentication method (password or certificate based)
        :param cluster_options: Options for configuring the cluster connection
        :param bucket: Name of the Couchbase bucket to use
        :param scope: Name of the scope within the bucket
        :param collection: Name of the collection within the scope
        :param vector_search_index: Name of the vector search index to use
        :param is_global_level_index: If True, uses a global (bucket-level) vector search index that can search across all
            scopes and collections. If False (default), uses a scope-level index that only searches within the specified scope.
        :param kwargs: Additional keyword arguments passed to the Cluster constructor
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
            is_global_level_index=self.is_global_level_index,
            **self._kwargs,
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CouchbaseSearchDocumentStore":
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

    def _get_search_interface(self):
        """
        Returns the appropriate search interface based on the index level configuration.

        :returns: Either scope.search_indexes() for scope-level or connection.search_indexes() for global-level
        """
        if not self.is_global_level_index:
            return self.scope.search_indexes()
        return self.connection.search_indexes()

    def count_documents(self) -> int:
        """
        Returns how many documents are present in the document store.

        :returns: The number of documents in the document store.
        """
        search_interface = self._get_search_interface()
        return search_interface.get_indexed_documents_count(self.vector_search_index)

    def filter_documents(self, filters: Optional[Dict[str, Any]] = None) -> List[Document]:
        """
        Returns the documents that match the filters provided.

        For a detailed specification of the filters,
        refer to the Haystack [documentation](https://docs.haystack.deepset.ai/v2.0/docs/metadata-filtering).

        :param filters: The filters to apply. It returns only the documents that match the filters.
        :returns: A list of Documents that match the given filters.
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
        search_query: SearchQuery = None,
        limit: Optional[int] = None,
    ) -> List[Document]:
        """
        Find the documents that are most similar to the provided `query_embedding` by using a vector similarity metric.

        :param query_embedding: Embedding of the query
        :param top_k: How many documents to be returned by the vector query
        :param search_query: Search filters param which is parsed to the Couchbase search query. The vector query and
        search query are ORed operation.
        :param limit: Maximum number of Documents to return. Defaults to top_k if not specified.
        :returns: A list of Documents that are most similar to the given `query_embedding`
        :raises ValueError: If `query_embedding` is empty
        :raises DocumentStoreError: If the retrieval of documents from Couchbase fails
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

        if not self.is_global_level_index:
            response = self.scope.search(self.vector_search_index, request, options)
        else:
            response = self.connection.search(self.vector_search_index, request, options)

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


class CouchbaseGSIDocumentStore(CouchbaseDocumentStore):
    """
    CouchbaseGSIDocumentStore is a DocumentStore implementation that uses
    Couchbase Global Secondary Index (GSI) for vector search capabilities.

    This document store supports two types of vector indexes:

    - BHIVE Index: A dedicated vector index for high-performance ANN vector search
    - Composite Secondary Index: Includes vectors alongside other fields for combined filtering

    Both index types support various vector similarity metrics and can be configured with
    additional parameters for optimizing vector search performance.
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
        index_name: str,
        index_type: IndexType = IndexType.BHIVE,
        vector_field: str = "embedding",
        index_params: IndexParams = None,
        **kwargs: Dict[str, Any],
    ):
        """
        Creates a new CouchbaseGSIDocumentStore instance.

        :param cluster_connection_string: Connection string for the Couchbase cluster
        :param authenticator: Authentication method (password or certificate based)
        :param cluster_options: Options for configuring the cluster connection
        :param bucket: Name of the Couchbase bucket to use
        :param scope: Name of the scope within the bucket
        :param collection: Name of the collection within the scope
        :param index_name: Name of the GSI index to use for vector search
        :param index_type: Type of index (BHIVE or COMPOSITE)
        :param vector_field: Name of the field containing vectors
        :param index_params: Parameters for configuring the vector index
        :param kwargs: Additional keyword arguments passed to the Cluster constructor
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
        self.index_name = index_name
        self.index_type = index_type
        self.vector_field = vector_field
        self.index_params = index_params or IndexParams()

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
            index_name=self.index_name,
            index_type=self.index_type,
            vector_field=self.vector_field,
            index_params=self.index_params.to_dict(),
            **self._kwargs,
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CouchbaseGSIDocumentStore":
        """
        Deserializes the component from a dictionary.

        :param data:
            Dictionary to deserialize from.
        :returns:
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
        
        # Handle index_params deserialization if present
        if "index_params" in init_params:
            init_params["index_params"] = IndexParams.from_dict(init_params["index_params"])
        
        # Handle secrets
        deserialize_secrets_inplace(init_params, keys=["cluster_connection_string"])
        
        return cls(**init_params)

    def create_index(self) -> None:
        """
        Creates a vector search index for the collection if it doesn't exist.
        The index type and configuration are based on the initialization parameters.
        
        For BHIVE index, creates a dedicated vector index.
        For Composite index, creates a secondary index that includes the vector field.
        
        :raises DocumentStoreError: If creating the index fails.
        """
        try:
            query_context = f"{self.bucket}.{self.scope_name}.{self.collection_name}"
            
            # Include fields formatted for the WITH clause
            include_clause = ""
            if self.index_params.include_fields:
                include_fields_str = ", ".join(self.index_params.include_fields)
                include_clause = f"INCLUDE ({include_fields_str})"
            
            # Get the index parameters as a dictionary for the WITH clause
            with_params = self.index_params.to_dict()
            # Remove include_fields from with_params as it's handled in the INCLUDE clause
            with_params.pop("include_fields", None)
            
            if self.index_type == IndexType.BHIVE:
                # Create BHIVE vector index
                query = f"""
                CREATE VECTOR INDEX {self.index_name}
                ON {query_context} ({self.vector_field} VECTOR)
                {include_clause}
                USING GSI
                WITH {with_params}
                """
            else:
                # Create Composite secondary index with vector field
                # Ensure description is set for composite index
                if "description" not in with_params and self.index_params.description:
                    with_params["description"] = self.index_params.description
                
                query = f"""
                CREATE INDEX {self.index_name}
                ON {query_context} ({self.vector_field} VECTOR)
                {include_clause}
                USING GSI
                WITH {with_params}
                """
            # Execute the query to create the index
            self.connection.query(query, QueryOptions(timeout=timedelta(seconds=60))).execute()
            logger.info(f"Created vector index '{self.index_name}' on {query_context}")
        except Exception as e:
            msg = f"Failed to create vector index: {e}"
            logger.error(msg)
            raise DocumentStoreError(msg) from e

    def drop_index(self) -> None:
        """
        Drops the vector search index if it exists.
        
        :raises DocumentStoreError: If dropping the index fails.
        """
        try:
            query_context = f"{self.bucket}.{self.scope_name}.{self.collection_name}.{self.index_name}"
            query = f"DROP INDEX {query_context}"
            self.connection.query(query).execute()
            logger.info(f"Dropped vector index '{self.index_name}'")
        except Exception as e:
            msg = f"Failed to drop vector index: {e}"
            logger.error(msg)
            raise DocumentStoreError(msg) from e

    def count_documents(self) -> int:
        """
        Returns how many documents are present in the document store.

        :returns: The number of documents in the document store.
        """
        query = f"SELECT COUNT(*) as count FROM {self.bucket}.{self.scope_name}.{self.collection_name}"
        result = self.connection.query(query)
        return result.rows()[0]["count"]

    def filter_documents(self, filters: Optional[Dict[str, Any]] = None) -> List[Document]:
        """
        Returns the documents that match the filters provided.

        For a detailed specification of the filters,
        refer to the Haystack [documentation](https://docs.haystack.deepset.ai/v2.0/docs/metadata-filtering).

        :param filters: The filters to apply. It returns only the documents that match the filters.
        :returns: A list of Documents that match the given filters.
        """
        query_str = f"SELECT d.*, meta().id as id FROM {self.bucket}.{self.scope_name}.{self.collection_name}"
        where_clause = ""
        
        if filters:
            normalized_filters = normalize_sql_filters(filters)
            where_clause = f" WHERE {normalized_filters}"
        
        query_str += where_clause
        
        try:
            result = self.connection.query(query_str, QueryOptions(timeout=timedelta(seconds=60)))
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
        limit: Optional[int] = None,
    ) -> List[Document]:
        """
        Find the documents that are most similar to the provided `query_embedding` by using a vector similarity metric.

        :param query_embedding: Embedding of the query
        :param top_k: How many documents to be returned by the vector query
        :param filters: Optional filters to apply before vector similarity search
        :param limit: Maximum number of Documents to return. Defaults to top_k if not specified.
        :returns: A list of Documents that are most similar to the given `query_embedding`
        :raises ValueError: If `query_embedding` is empty
        :raises DocumentStoreError: If the retrieval of documents from Couchbase fails
        """
        if not query_embedding:
            msg = "Query embedding must not be empty"
            raise ValueError(msg)

        if len(query_embedding) != self.index_params.dimension:
            msg = f"Query embedding dimension {len(query_embedding)} does not match index dimension {self.index_params.dimension}"
            raise ValueError(msg)

        if limit is None:
            limit = top_k

        # Construct the SQL++ query with vector search
        query_context = f"{self.bucket}.{self.scope_name}.{self.collection_name}"
        
        # Convert embedding to string representation for query
        query_vector_str = str(query_embedding)
        
        # Handle filters if provided
        where_clause = ""
        if filters:
            normalized_filters = normalize_sql_filters(filters)
            where_clause = f"WHERE {normalized_filters}"
        
        # Build the query
        if self.index_type == IndexType.BHIVE:
            # Use APPROX_VECTOR_DISTANCE for BHIVE index
            query_str = f"""
            SELECT d.*, meta().id as id
            FROM {query_context} d
            {where_clause}
            ORDER BY APPROX_VECTOR_DISTANCE(d.{self.vector_field}, {query_vector_str}, 
                                             "{self.index_params.similarity}", {limit})
            LIMIT {limit}
            """
        else:
            # Use standard vector distance for composite index
            query_str = f"""
            SELECT d.*, meta().id as id
            FROM {query_context} d
            {where_clause}
            ORDER BY APPROX_VECTOR_DISTANCE(d.{self.vector_field}, {query_vector_str}, 
                                             "{self.index_params.similarity}", {limit})
            LIMIT {limit}
            """
        
        try:
            # Execute the query
            result: QueryResult = self.connection.query(
                query_str, 
                QueryOptions(timeout=timedelta(seconds=60))
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
            
    def vector_search(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Document]:
        """
        Find the documents that are most similar to the provided `query_embedding` using GSI vector search.

        This method uses the appropriate vector search function based on the index type:
        - For BHIVE indexes: Uses APPROX_VECTOR_DISTANCE for approximate nearest neighbor search
        - For Composite indexes: Uses VECTOR_DISTANCE for exact vector search

        :param query_embedding: Embedding vector of the query
        :param top_k: Maximum number of documents to return
        :param filters: Optional filters to apply to documents before vector search
        :returns: List of Documents most similar to the query embedding, sorted by relevance
        :raises ValueError: If query_embedding is empty or has wrong dimension
        :raises DocumentStoreError: If vector search fails
        """
        return self._embedding_retrieval(
            query_embedding=query_embedding,
            top_k=top_k,
            filters=filters,
        )
