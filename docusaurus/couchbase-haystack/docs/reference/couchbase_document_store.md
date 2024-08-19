---
id: couchbase_document_store
title: CouchbaseDocumentStore
---

# CouchbaseDocumentStore

`CouchbaseDocumentStore` is a DocumentStore implementation designed to interact with the [Couchbase Capella](https://cloud.couchbase.com) service or [Couchbase server](https://www.couchbase.com/products/server). This implementation allows you to efficiently store and retrieve documents, taking advantage of Couchbase’s scalable and high-performance capabilities. Document properties are stored within Couchbase collections, and embeddings for dense retrievals can be stored as part of the document attributes. This implementation is based on the [Couchbase Python SDK](https://docs.couchbase.com/python-sdk/current/hello-world/start-using-sdk.html), ensuring smooth integration and operation.


## Installation

```bash
pip install couchbase-haystack
```

## Class: `CouchbaseDocumentStore`

### `__init__`

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
    **kwargs: Dict[str, Any]
) -> None
```

Creates a new `CouchbaseDocumentStore` instance.

**Parameters:**

- `cluster_connection_string` (Secret): The connection string for the Couchbase cluster.
- `authenticator` (Union[CouchbasePasswordAuthenticator, CouchbaseCertificateAuthenticator]): The authenticator to use.
- `cluster_options` (CouchbaseClusterOptions): The options for the Couchbase cluster.
- `bucket` (str): The bucket name.
- `scope` (str): The scope name.
- `collection` (str): The collection name.
- `vector_search_index` (str): The index for vector search.

**Raises:**

- `ValueError`: If the collection name contains invalid characters.

### `to_dict`

```python
def to_dict(self) -> Dict[str, Any]:
```

Serializes the component to a dictionary.

**Returns:**

- `Dict[str, Any]`: Dictionary with serialized data.

### `from_dict`

```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> "CouchbaseDocumentStore":
```

Deserializes the component from a dictionary.

**Parameters:**

- `data` (Dict[str, Any]): Dictionary to deserialize from.

**Returns:**

- `CouchbaseDocumentStore`: Deserialized component.

### `count_documents`

```python
def count_documents(self) -> int:
```

Returns how many documents are present in the document store.

**Returns:**

- `int`: The number of documents in the document store.

### `filter_documents`

```python
def filter_documents(self, filters: Optional[Dict[str, Any]] = None) -> List[Document]:
```

Returns the documents that match the filters provided.

**Parameters:**

- `filters` (Optional[Dict[str, Any]]): The filters to apply.

**Returns:**

- `List[Document]`: A list of Documents that match the given filters.

### `write_documents`

```python
def write_documents(self, documents: List[Document], policy: DuplicatePolicy = DuplicatePolicy.NONE) -> int:
```

Writes documents into the Couchbase collection.

**Parameters:**

- `documents` (List[Document]): A list of Documents to write to the document store.
- `policy` (DuplicatePolicy): The duplicate policy to use when writing documents.

**Raises:**

- `DuplicateDocumentError`: If a document with the same ID already exists and the policy is `DuplicatePolicy.FAIL`.
- `ValueError`: If the documents are not of type Document.

**Returns:**

- `int`: The number of documents written to the document store.

### `delete_documents`

```python
def delete_documents(self, document_ids: List[str]) -> None:
```

Deletes all documents with matching `document_ids` from the document store.

**Parameters:**

- `document_ids` (List[str]): The document IDs to delete.

### `_embedding_retrieval`

```python
def _embedding_retrieval(
    self,
    query_embedding: List[float],
    top_k: int = 10,
    search_query: SearchQuery = None,
    limit: Optional[int] = None,
) -> List[Document]:
```

Finds the documents most similar to the provided `query_embedding` by using a vector similarity metric.

**Parameters:**

- `query_embedding` (List[float]): Embedding of the query.
- `top_k` (int): How many documents to be returned by the vector query.
- `search_query` (SearchQuery): Search filters parsed to the Couchbase search query.
- `limit` (Optional[int]): Maximum number of Documents to return.

**Returns:**

- `List[Document]`: A list of Documents most similar to the given `query_embedding`.

**Raises:**

- `ValueError`: If `query_embedding` is empty.
- `DocumentStoreError`: If the retrieval of documents from Couchbase fails.

### `__getDocFromKV`

```python
def __getDocFromKV(self, response: SearchResult) -> List[Document]:
```

Retrieves documents from Couchbase Key-Value store based on a search response.

**Parameters:**

- `response` (SearchResult): The search result from Couchbase.

**Returns:**

- `List[Document]`: A list of Documents retrieved from the Key-Value store.