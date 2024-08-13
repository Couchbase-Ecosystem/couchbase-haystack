# SPDX-FileCopyrightText: 2023-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0
from typing import Any, Dict, List, Optional, Union

from haystack import component, default_from_dict, default_to_dict
from haystack.dataclasses import Document
from couchbase.search import SearchQuery
from couchbase_haystack.document_stores import CouchbaseDocumentStore

@component
class CouchbaseEmbeddingRetriever:
    """
    Retrieves documents from the CouchbaseDocumentStore by embedding similarity.

    The similarity is dependent on the vector_search_index used in the CouchbaseDocumentStore and the chosen metric
    during the creation of the index (i.e. dot product, or l2 norm). See CouchbaseDocumentStore for more
    information.

    Usage example:
    ```python
    import numpy as np
    from couchbase_haystack import CouchbaseDocumentStore, CouchbaseEmbeddingRetriever

    store = CouchbaseDocumentStore(cluster_connection_string="couchbases://localhost",
        cluster_options=CouchbaseClusterOptions(),
        authenticator=CouchbasePasswordAuthenticator(),
        bucket="haystack_test_bucket",
        scope="scope_name",
        collection="collection_name",
        vector_search_index="vector_index")
    retriever = CouchbaseEmbeddingRetriever(document_store=store)

    results = retriever.run(query_embedding=np.random.random(768).tolist())
    print(results["documents"])
    ```

    The example above retrieves the 10 most similar documents to a random query embedding from the
    CouchbaseDocumentStore. Note that dimensions of the query_embedding must match the dimensions of the embeddings
    stored in the CouchbaseDocumentStore.
    """

    def __init__(
        self,
        *,
        document_store: CouchbaseDocumentStore,
        top_k: int = 10,
    ):
        """
        Create the CouchbaseDocumentStore component.

        Note: Currently, the filter option is not supported with embedding queries. 
        Instead, you can provide a couchbase search query while running the embedding query. 
        The embedding query and search query are combined using an OR operation.

        :param document_store: An instance of CouchbaseDocumentStore.
        :param top_k: Maximum number of Documents to return.

        :raises ValueError: If `document_store` is not an instance of `CouchbaseDocumentStore`.
        """
        if not isinstance(document_store, CouchbaseDocumentStore):
            msg = "document_store must be an instance of CouchbaseDocumentStore"
            raise ValueError(msg)

        self.document_store = document_store
        self.top_k = top_k

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes the component to a dictionary.

        :returns:
            Dictionary with serialized data.
        """
        return default_to_dict(
            self,
            top_k=self.top_k,
            document_store=self.document_store.to_dict(),
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CouchbaseEmbeddingRetriever":
        """
        Deserializes the component from a dictionary.

        :param data:
            Dictionary to deserialize from.
        :returns:
              Deserialized component.
        """
        data["init_parameters"]["document_store"] = CouchbaseDocumentStore.from_dict(
            data["init_parameters"]["document_store"]
        )
        return default_from_dict(cls, data)

    @component.output_types(documents=List[Document])
    def run(
        self,
        query_embedding: List[float],
        top_k: Optional[int] = None,
        search_query: Optional[SearchQuery] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, List[Document]]:
        """
        Retrieve documents from the CouchbaseDocumentStore, based on the provided embedding similarity.

        :param query_embedding: Embedding of the query.
        :param filters: Filters applied to the retrieved Documents. The way runtime filters are applied depends on
                        the `filter_policy` chosen at document store initialization. See init method docstring for more
                        details.              
        :param top_k: Maximum number of Documents to be returned from vector query. Overrides the value specified at initialization.
        :param search: Search filters param which is parsed to the Couchbase search query. The vector query and search query are ORed operation.
        :param limit: Maximum number of Documents to be return by the couchbase fts search request. Default value is top_k. 
        :returns: A dictionary with the following keys:
            - `documents`: List of Documents most similar to the given `query_embedding`
        """
        
        top_k = top_k or self.top_k

        docs = self.document_store._embedding_retrieval(
            query_embedding=query_embedding,
            top_k=top_k,
            search_query=search_query,
            limit = limit
        )
        return {"documents": docs}
