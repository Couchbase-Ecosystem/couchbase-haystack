---
id: couchbase_document_store
title: CouchbaseDocumentStore
---

# CouchbaseDocumentStore

`CouchbaseDocumentStore` is a DocumentStore implementation designed to interact with the [Couchbase Capella](https://cloud.couchbase.com) service or [Couchbase server](https://www.couchbase.com/products/server). This implementation allows you to efficiently store and retrieve documents, taking advantage of Couchbase’s scalable and high-performance capabilities. Document properties are stored within Couchbase collections, and embeddings for dense retrievals can be stored as part of the document attributes. This implementation is based on the [Couchbase Python SDK](https://docs.couchbase.com/python-sdk/current/hello-world/start-using-sdk.html), ensuring smooth integration and operation.


## Installation

To use the `CouchbaseDocumentStore`, make sure you have the necessary dependencies installed:

```bash
pip install couchbase-haystack
```

## Getting Started

### Initialization

To create an instance of `CouchbaseDocumentStore`, you need to provide connection details, authentication credentials, and specify the bucket, scope, collection, and vector search index.

```python
from haystack.document_stores.couchbase import CouchbaseDocumentStore
from haystack.utils.auth import Secret
from couchbase.options import ClusterOptions
from couchbase.auth import CouchbasePasswordAuthenticator

# Initialize CouchbaseDocumentStore
document_store = CouchbaseDocumentStore(
    cluster_connection_string=Secret.from_env_var("CB_CONNECTION_STRING"),
    authenticator=CouchbasePasswordAuthenticator(
            username=Secret.from_env_var("CB_USERNAME"),
            password=Secret.from_env_var("CB_PASSWORD")
    ),
    bucket="my_bucket",
    scope="my_scope",
    collection="my_collection",
    vector_search_index="my_vector_index"
)
```

### Method Overview

#### `__init__`

```python
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
```

**Input Parameters:**
- `cluster_connection_string` (Secret): Connection string for the Couchbase cluster.
- `authenticator` (Union[CouchbasePasswordAuthenticator, CouchbaseCertificateAuthenticator]): Authenticator for Couchbase.
- `cluster_options` (CouchbaseClusterOptions): Additional options for the Couchbase cluster.
- `bucket` (str): The name of the bucket to connect to.
- `scope` (str): The name of the scope within the bucket.
- `collection` (str): The name of the collection within the scope.
- `vector_search_index` (str): The index name for vector search.

**Raises:**
- `ValueError`: If the collection name contains invalid characters.

#### `write_documents`

```python
def write_documents(
    documents: List[Document],
    policy: DuplicatePolicy = DuplicatePolicy.NONE
) -> int:
```

**Input Parameters:**
- `documents` (List[Document]): A list of `Document` objects to be written to the Couchbase collection.
- `policy` (DuplicatePolicy): The policy for handling duplicate documents. Can be:
  - `DuplicatePolicy.FAIL`: Raises an error if a document with the same ID already exists.
  - `DuplicatePolicy.OVERWRITE`: Overwrites any existing documents with the same ID.
  - `DuplicatePolicy.NONE`: Equivalent to `FAIL`.

**Response:**
- Returns an `int` representing the number of documents successfully written to the document store.

**Raises:**
- `DuplicateDocumentError`: If a document with the same ID already exists and the policy is set to `FAIL`.
- `ValueError`: If the documents are not of type `Document`.
- `DocumentStoreError`: For other errors encountered during the write operation.

**Example Usage:**

```python
documents = [
    Document(content="Document 1 content", id="doc1"),
    Document(content="Document 2 content", id="doc2"),
]

written_count = document_store.write_documents(documents, policy=DuplicatePolicy.OVERWRITE)
```

#### `filter_documents`

```python
def filter_documents(filters: Optional[Dict[str, Any]] = None) -> List[Document]:
```

**Input Parameters:**
- `filters` (Optional[Dict[str, Any]]): A dictionary of filters to apply when retrieving documents. The keys should correspond to metadata fields, and the values should be lists of acceptable values.

**Response:**
- Returns a `List[Document]` containing documents that match the provided filters.

**Example Usage:**

```python
filters = {"author": ["John Doe"], "year": ["2024"]}
documents = document_store.filter_documents(filters=filters)
```

**Output:**
- A list of `Document` objects that match the specified filters.

#### `count_documents`

```python
def count_documents() -> int:
```

**Response:**
- Returns an `int` representing the number of documents present in the document store.

**Example Usage:**

```python
doc_count = document_store.count_documents()
```

**Output:**
- The total number of documents in the document store.

#### `delete_documents`

```python
def delete_documents(document_ids: List[str]) -> None:
```

**Input Parameters:**
- `document_ids` (List[str]): A list of document IDs to delete from the document store.

**Response:**
- This method does not return any value (`None`).

**Example Usage:**

```python
document_store.delete_documents(document_ids=["doc1", "doc2"])
```

**Note:** If `document_ids` is an empty list, no action will be taken.

#### `_embedding_retrieval`

```python
def _embedding_retrieval(
    query_embedding: List[float],
    top_k: int = 10,
    search_query: SearchQuery = None,
    limit: Optional[int] = None,
) -> List[Document]:
```

**Input Parameters:**
- `query_embedding` (List[float]): A list of float values representing the query embedding.
- `top_k` (int): The number of top documents to return based on similarity to the query embedding. Default is 10.
- `search_query` (Optional[SearchQuery]): Additional search filters to apply along with the vector search. Default is `None`.
- `limit` (Optional[int]): Maximum number of documents to return. Default is `top_k`.

**Response:**
- Returns a `List[Document]` containing the documents most similar to the provided `query_embedding`.

**Raises:**
- `ValueError`: If the `query_embedding` is empty.
- `DocumentStoreError`: If there is an error retrieving documents from Couchbase.

**Example Usage:**

```python
query_embedding = [0.1, 0.2, 0.3, ...]  # Example embedding vector
similar_documents = document_store._embedding_retrieval(query_embedding=query_embedding, top_k=5)
```

**Output:**
- A list of `Document` objects that are most similar to the given `query_embedding`.

### Serialization Methods

#### `to_dict`

```python
def to_dict() -> Dict[str, Any]:
```

**Response:**
- Returns a `Dict[str, Any]` containing the serialized state of the `CouchbaseDocumentStore` instance.

**Example Usage:**

```python
serialized_data = document_store.to_dict()
```

#### `from_dict`

```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> "CouchbaseDocumentStore":
```

**Input Parameters:**
- `data` (Dict[str, Any]): A dictionary containing the serialized state of a `CouchbaseDocumentStore`.

**Response:**
- Returns a `CouchbaseDocumentStore` instance reconstructed from the provided dictionary.

**Example Usage:**

```python
new_document_store = CouchbaseDocumentStore.from_dict(serialized_data)
```
