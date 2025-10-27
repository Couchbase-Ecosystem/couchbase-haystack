# SPDX-FileCopyrightText: 2023-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0
from typing import Any, Dict, List, Optional

from couchbase.search import SearchQuery
from haystack import component, default_from_dict, default_to_dict
from haystack.dataclasses import Document

from couchbase_haystack.document_stores import (
    CouchbaseQueryDocumentStore,
    CouchbaseSearchDocumentStore,
)


@component
class CouchbaseSearchEmbeddingRetriever:
    """Retrieves documents from the CouchbaseSearchDocumentStore by embedding similarity.

    The similarity is dependent on the vector_search_index used in the CouchbaseSearchDocumentStore and the chosen metric
    during the creation of the index (i.e. dot product, or l2 norm). See CouchbaseSearchDocumentStore for more
    information.

    Usage example:

    ```python
    import numpy as np
    from couchbase_haystack import CouchbaseSearchDocumentStore, CouchbaseSearchEmbeddingRetriever, CouchbasePasswordAuthenticator
    from haystack.utils import Secret

    store = CouchbaseSearchDocumentStore(
        cluster_connection_string=Secret.from_env_var("CB_CONNECTION_STRING"),
        authenticator=CouchbasePasswordAuthenticator(
            username=Secret.from_env_var("CB_USERNAME"),
            password=Secret.from_env_var("CB_PASSWORD")
        ),
        bucket="haystack_test_bucket",
        scope="scope_name",
        collection="collection_name",
        vector_search_index="vector_index"
    )
    retriever = CouchbaseSearchEmbeddingRetriever(document_store=store)

    results = retriever.run(query_embedding=np.random.random(768).tolist())
    print(results["documents"])
    ```

    The example above retrieves the 10 most similar documents to a random query embedding from the
    CouchbaseSearchDocumentStore. Note that dimensions of the query_embedding must match the dimensions of the embeddings
    stored in the CouchbaseSearchDocumentStore.
    """

    def __init__(
        self,
        *,
        document_store: CouchbaseSearchDocumentStore,
        top_k: int = 10,
    ):
        """Create the CouchbaseSearchDocumentStore component.

        Note: Currently, the filter option is not supported with embedding queries.
        Instead, you can provide a couchbase search query while running the embedding query.
        The embedding query and search query are combined using an OR operation.

        Args:
            document_store: An instance of CouchbaseSearchDocumentStore.
            top_k: Maximum number of Documents to return.

        Raises:
            ValueError: If document_store is not an instance of CouchbaseSearchDocumentStore.
        """
        if not isinstance(document_store, CouchbaseSearchDocumentStore):
            msg = "document_store must be an instance of CouchbaseSearchDocumentStore"
            raise ValueError(msg)

        self.document_store = document_store
        self.top_k = top_k

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the component to a dictionary.

        Returns:
            Dictionary with serialized data.
        """
        return default_to_dict(
            self,
            top_k=self.top_k,
            document_store=self.document_store.to_dict(),
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CouchbaseSearchEmbeddingRetriever":
        """Deserializes the component from a dictionary.

        Args:
            data: Dictionary to deserialize from.

        Returns:
            Deserialized component.
        """
        data["init_parameters"]["document_store"] = CouchbaseSearchDocumentStore.from_dict(
            data["init_parameters"]["document_store"]
        )
        return default_from_dict(cls, data)

    @component.output_types(documents=List[Document])
    def run(
        self,
        query_embedding: List[float],
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
        search_query: Optional[SearchQuery] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, List[Document]]:
        """Retrieve documents from the CouchbaseSearchDocumentStore, based on the provided embedding similarity.

        Args:
            query_embedding: Embedding of the query.
            top_k: Maximum number of Documents to be returned from vector query.
                  Overrides the value specified at initialization.
            filters: Optional dictionary of filters to apply before the vector search.
                     Refer to Haystack documentation for filter structure (https://docs.haystack.deepset.ai/v2.0/docs/metadata-filtering).
            search_query: Search filters param which is parsed to the Couchbase search query.
                        The vector query and search query are ORed operation.
            limit: Maximum number of Documents to be return by the couchbase fts search request.
                  Default value is top_k.

        Returns:
            A dictionary with the following keys:
            - documents: List of Documents most similar to the given query_embedding
        """
        top_k = top_k or self.top_k

        docs = self.document_store._embedding_retrieval(
            query_embedding=query_embedding, top_k=top_k, search_query=search_query, filters=filters, limit=limit
        )
        return {"documents": docs}


@component
class CouchbaseQueryEmbeddingRetriever:
    """Retrieves documents from the CouchbaseQueryDocumentStore using vector similarity search with GSI indexes.

    The similarity metric used depends on the configuration of the GSI index in Couchbase
    (e.g., dot product, cosine similarity, squared Euclidean). See CouchbaseQueryDocumentStore for more details.

    Usage example:

    ```python
    import numpy as np
    from couchbase_haystack import (
        CouchbaseQueryDocumentStore,
        CouchbaseQueryEmbeddingRetriever,
        CouchbasePasswordAuthenticator,
        QueryVectorSearchType,
        CouchbaseQueryOptions,
        QueryVectorSearchSimilarity
    )
    from haystack.utils import Secret

    # Assume a Couchbase GSI index named "vector_gsi_index" exists on the "embedding" field
    # with dimension 768 and using cosine similarity.
    store = CouchbaseQueryDocumentStore(
        cluster_connection_string=Secret.from_env_var("CB_CONNECTION_STRING"),
        authenticator=CouchbasePasswordAuthenticator(
            username=Secret.from_env_var("CB_USERNAME"),
            password=Secret.from_env_var("CB_PASSWORD")
        ),
        bucket="haystack_test_bucket",
        scope="scope_name",
        collection="collection_name",
        search_type=QueryVectorSearchType.ANN, # Or KNN depending on index
        similarity=QueryVectorSearchSimilarity.COSINE, # Or DOT, L2, EUCLIDEAN, L2_SQUARED or EUCLIDEAN_SQUARED
        nprobes=10, # optional Number of probes for the ANN search
        query_options=CouchbaseQueryOptions() # Optional query options
    )
    retriever = CouchbaseQueryEmbeddingRetriever(document_store=store, top_k=5)

    # Generate a random query embedding matching the dimension
    random_embedding = np.random.rand(768).tolist()

    # Example without filters
    results_no_filter = retriever.run(query_embedding=random_embedding)
    print("Documents found without filters:", results_no_filter["documents"])

    # Example with filters
    filters = {"field": "meta.genre", "operator": "==", "value": "fiction"}
    results_with_filter = retriever.run(query_embedding=random_embedding, filters=filters)
    print("Documents found with filters:", results_with_filter["documents"])
    ```

    The example above retrieves the 5 most similar documents to a random query embedding from the
    CouchbaseQueryDocumentStore. Note that the dimensions of the `query_embedding` must match the dimensions
    configured in the `query_vector_search_params` of the `CouchbaseQueryDocumentStore`.
    Filters are applied before the vector search.
    """

    def __init__(
        self,
        *,
        document_store: CouchbaseQueryDocumentStore,
        top_k: int = 10,
    ):
        """Create the CouchbaseQueryEmbeddingRetriever component.

        Args:
            document_store: An instance of CouchbaseQueryDocumentStore.
            top_k: Maximum number of Documents to return based on vector similarity.

        Raises:
            ValueError: If document_store is not an instance of CouchbaseQueryDocumentStore.
        """
        if not isinstance(document_store, CouchbaseQueryDocumentStore):
            msg = "document_store must be an instance of CouchbaseQueryDocumentStore"
            raise ValueError(msg)

        self.document_store = document_store
        self.top_k = top_k

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the component to a dictionary.

        Returns:
            Dictionary with serialized data.
        """
        return default_to_dict(
            self,
            top_k=self.top_k,
            document_store=self.document_store.to_dict(),
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CouchbaseQueryEmbeddingRetriever":
        """Deserializes the component from a dictionary.

        Args:
            data: Dictionary to deserialize from.

        Returns:
            Deserialized component.
        """
        data["init_parameters"]["document_store"] = CouchbaseQueryDocumentStore.from_dict(
            data["init_parameters"]["document_store"]
        )
        return default_from_dict(cls, data)

    @component.output_types(documents=List[Document])
    def run(
        self,
        query_embedding: List[float],
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
        nprobes: Optional[int] = None,
    ) -> Dict[str, List[Document]]:
        """Retrieve documents from the CouchbaseQueryDocumentStore based on embedding similarity using GSI.

        Args:
            query_embedding: Embedding of the query.
            top_k: Maximum number of Documents to be returned based on similarity score.
                   Overrides the value specified at initialization.
            filters: Optional dictionary of filters to apply before the vector search.
                     Refer to Haystack documentation for filter structure (https://docs.haystack.deepset.ai/v2.0/docs/metadata-filtering).
            nprobes: Number of probes for the ANN search. If None, uses the value set at index creation time
            or the value set at the document store level.
        Returns:
            A dictionary with the following keys:
            - documents: List of Documents most similar to the given `query_embedding`, potentially filtered.
        """
        top_k = top_k or self.top_k

        docs = self.document_store._embedding_retrieval(
            query_embedding=query_embedding, top_k=top_k, filters=filters, nprobes=nprobes
        )
        return {"documents": docs}
