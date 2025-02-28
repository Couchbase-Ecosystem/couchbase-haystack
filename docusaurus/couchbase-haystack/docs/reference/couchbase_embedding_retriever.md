---
id: couchbase_search_embedding_retriever
title: CouchbaseSearchEmbeddingRetriever
---

```markdown
# Couchbase Search Embedding Retriever

## Class Overview

### `CouchbaseSearchEmbeddingRetriever`

The `CouchbaseSearchEmbeddingRetriever` retrieves documents from the `CouchbaseSearchDocumentStore` by embedding similarity. The similarity depends on the `vector_search_index` used in the `CouchbaseSearchDocumentStore` and the metric chosen during the creation of the index (e.g., dot product, or L2 norm).

#### Initialization

```python
def __init__(
    self,
    *,
    document_store: CouchbaseSearchDocumentStore,
    top_k: int = 10,
)
```

**Input Parameters:**
- `document_store` (CouchbaseSearchDocumentStore): An instance of `CouchbaseSearchDocumentStore` where the documents are stored.
- `top_k` (int): Maximum number of documents to return. Defaults to 10.

**Raises:**
- `ValueError`: If `document_store` is not an instance of `CouchbaseSearchDocumentStore`.

**Example Usage:**

```python
import numpy as np
from couchbase_haystack import CouchbaseSearchDocumentStore, CouchbaseSearchEmbeddingRetriever
from haystack.utils.auth import Secret

store = CouchbaseSearchDocumentStore(
    cluster_connection_string=Secret.from_env_var("CB_CONNECTION_STRING"),,
    cluster_options=CouchbaseClusterOptions(),
    authenticator=CouchbasePasswordAuthenticator(),
    bucket="haystack_test_bucket",
    scope="scope_name",
    collection="collection_name",
    vector_search_index="vector_index"
)

retriever = CouchbaseSearchEmbeddingRetriever(document_store=store)

query_embedding = np.random.random(768).tolist()
results = retriever.run(query_embedding=query_embedding)
print(results["documents"])
```

#### `run`

```python
@component.output_types(documents=List[Document])
def run(
    self,
    query_embedding: List[float],
    top_k: Optional[int] = None,
    search_query: Optional[SearchQuery] = None,
    limit: Optional[int] = None,
) -> Dict[str, List[Document]]
```

**Description:**
- Retrieves documents from the `CouchbaseSearchDocumentStore` based on the similarity of their embeddings to the provided query embedding.

**Input Parameters:**
- `query_embedding` (List[float]): A list of float values representing the query embedding. The dimensionality of this embedding must match the dimensionality of the embeddings stored in the `CouchbaseSearchDocumentStore`.
- `top_k` (Optional[int]): The maximum number of documents to return. Overrides the value specified during initialization. Defaults to the value of `top_k` set during initialization.
- `search_query` (Optional[SearchQuery]): An optional search query to combine with the embedding query. The embedding query and search query are combined using an OR operation.
- `limit` (Optional[int]): The maximum number of documents to return from the Couchbase full-text search (FTS) query. Defaults to `top_k`.

**Response:**
- Returns a dictionary with a single key, `documents`, which maps to a list of `Document` objects that are most similar to the provided `query_embedding`.

**Example Usage:**

```python
query_embedding = [0.1, 0.2, 0.3, ...]  # Example embedding vector
results = retriever.run(query_embedding=query_embedding, top_k=5)
print(results["documents"])
```

#### `to_dict`

```python
def to_dict() -> Dict[str, Any]
```

**Description:**
- Serializes the `CouchbaseSearchEmbeddingRetriever` instance into a dictionary format.

**Response:**
- Returns a dictionary containing the serialized state of the `CouchbaseSearchEmbeddingRetriever` instance.

**Example Usage:**

```python
retriever_dict = retriever.to_dict()
```

#### `from_dict`

```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> "CouchbaseSearchEmbeddingRetriever"
```

**Description:**
- Deserializes a `CouchbaseSearchEmbeddingRetriever` instance from a dictionary.

**Input Parameters:**
- `data` (Dict[str, Any]): A dictionary containing the serialized state of a `CouchbaseSearchEmbeddingRetriever`.

**Response:**
- Returns a `CouchbaseSearchEmbeddingRetriever` instance reconstructed from the provided dictionary.

**Example Usage:**

```python
retriever_instance = CouchbaseSearchEmbeddingRetriever.from_dict(retriever_dict)
```

## Usage Example

```python
import numpy as np
from couchbase_haystack import CouchbaseSearchDocumentStore, CouchbaseSearchEmbeddingRetriever

store = CouchbaseSearchDocumentStore(
    cluster_connection_string="couchbases://localhost",
    cluster_options=CouchbaseClusterOptions(),
    authenticator=CouchbasePasswordAuthenticator(),
    bucket="haystack_test_bucket",
    scope="scope_name",
    collection="collection_name",
    vector_search_index="vector_index"
)

retriever = CouchbaseSearchEmbeddingRetriever(document_store=store)

query_embedding = np.random.random(768).tolist()
results = retriever.run(query_embedding=query_embedding)
print(results["documents"])
```

This example retrieves the 10 most similar documents to a randomly generated query embedding from the `CouchbaseSearchDocumentStore`. Note that the dimensionality of the `query_embedding` must match the dimensionality of the embeddings stored in the `CouchbaseSearchDocumentStore`.