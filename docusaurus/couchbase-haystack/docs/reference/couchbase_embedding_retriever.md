---
id: couchbase_embedding_retriever
title: CouchbaseEmbeddingRetriever
---

## Overview

The `CouchbaseEmbeddingRetriever` component retrieves documents from the `CouchbaseDocumentStore` by embedding similarity. The similarity is dependent on the vector search index used in the `CouchbaseDocumentStore` and the chosen metric during the creation of the index (e.g., dot product or L2 norm).

## Usage Example

```python
import numpy as np
from couchbase_haystack import CouchbaseDocumentStore, CouchbaseEmbeddingRetriever

store = CouchbaseDocumentStore(
    cluster_connection_string="couchbases://localhost",
    cluster_options=CouchbaseClusterOptions(),
    authenticator=CouchbasePasswordAuthenticator(),
    bucket="haystack_test_bucket",
    scope="scope_name",
    collection="collection_name",
    vector_search_index="vector_index"
)
retriever = CouchbaseEmbeddingRetriever(document_store=store)

results = retriever.run(query_embedding=np.random.random(768).tolist())
print(results["documents"])
```

The example above retrieves the 10 most similar documents to a random query embedding from the `CouchbaseDocumentStore`. Note that the dimensions of the `query_embedding` must match the dimensions of the embeddings stored in the `CouchbaseDocumentStore`.

## Class: `CouchbaseEmbeddingRetriever`

### `__init__`

```python
def __init__(
    self,
    *,
    document_store: CouchbaseDocumentStore,
    top_k: int = 10,
):
```

#### Parameters:

- **`document_store`** (`CouchbaseDocumentStore`): An instance of `CouchbaseDocumentStore`. The document store from which to retrieve documents.
- **`top_k`** (`int`): Maximum number of documents to return. Default is `10`.

#### Raises:

- **`ValueError`**: If `document_store` is not an instance of `CouchbaseDocumentStore`.

### Methods

#### `to_dict`

```python
def to_dict(self) -> Dict[str, Any]:
```

Serializes the component to a dictionary.

**Returns:**

- **`Dict[str, Any]`**: Dictionary with serialized data.

#### `from_dict`

```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> "CouchbaseEmbeddingRetriever":
```

Deserializes the component from a dictionary.

**Parameters:**

- **`data`** (`Dict[str, Any]`): Dictionary to deserialize from.

**Returns:**

- **`CouchbaseEmbeddingRetriever`**: Deserialized component.

#### `run`

```python
@component.output_types(documents=List[Document])
def run(
    self,
    query_embedding: List[float],
    top_k: Optional[int] = None,
    search_query: Optional[SearchQuery] = None,
    limit: Optional[int] = None,
) -> Dict[str, List[Document]]:
```

Retrieves documents from the `CouchbaseDocumentStore` based on the provided embedding similarity.

**Parameters:**

- **`query_embedding`** (`List[float]`): Embedding of the query.
- **`top_k`** (`Optional[int]`): Maximum number of documents to be returned from the vector query. Overrides the value specified at initialization.
- **`search_query`** (`Optional[SearchQuery]`): Search filters param which is parsed to the Couchbase search query. The vector query and search query are ORed operation.
- **`limit`** (`Optional[int]`): Maximum number of documents to be returned by the Couchbase FTS search request. Default value is `top_k`.

**Returns:**

- **`Dict[str, List[Document]]`**: A dictionary with the following keys:
  - `documents`: List of documents most similar to the given `query_embedding`.

## Notes

- The `CouchbaseEmbeddingRetriever` does not currently support filters with embedding queries. Instead, you can provide a Couchbase search query which will be combined with the embedding query using an OR operation.
```

### How to Use This Page
- **Copy and paste** this content into your Docusaurus Markdown file (e.g., `couchbase-embedding-retriever.md`).
- **Customize** the content as needed, especially if you want to add more examples, usage scenarios, or detailed explanations.
- **Link to GitHub**: If you wish to add links to the source code on GitHub, you can embed links directly into the method descriptions.

This documentation is structured to be clear and detailed, making it easy for users to understand the available methods and how to use the `CouchbaseEmbeddingRetriever` class.