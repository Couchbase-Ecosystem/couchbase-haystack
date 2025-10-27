<h1 align="center">couchbase-haystack</h1>

<p align="center">A <a href="https://docs.haystack.deepset.ai/docs/document_store"><i>Haystack</i></a> Document Store for <a href="https://www.couchbase.com"><i>Couchbase</i></a>.</p>

<p align="center">
  <a href="https://github.com/Couchbase-Ecosystem/couchbase-haystack/actions?query=workflow%3Aci">
    <img alt="ci" src="https://github.com/Couchbase-Ecosystem/couchbase-haystack/actions/workflows/ci.yml/badge.svg" />
  </a>
  <a href="https://couchbase-ecosystem.github.io/couchbase-haystack/">
    <img alt="documentation" src="https://img.shields.io/badge/docs-mkdocs%20material-blue.svg?style=flat" />
  </a>
  <a href="https://pypi.org/project/couchbase-haystack/">
    <img alt="pypi version" src="https://img.shields.io/pypi/v/couchbase-haystack.svg" />
  </a>
  <a href="https://pypi.org/project/haystack-ai/">
    <img alt="haystack version" src="https://img.shields.io/pypi/v/haystack-ai.svg?label=haystack" />
  </a>
</p>

----

**Table of Contents**

- [Breaking Changes in Version 2.0.0](#breaking-changes-in-version-200)
- [Overview](#overview)
- [Choosing the Right Document Store](#choosing-the-right-document-store)
- [Installation](#installation)
- [Usage](#usage)
  - [Running Couchbase](#running-couchbase)
  - [CouchbaseSearchDocumentStore (FTS-based)](#couchbasesearchdocumentstore-fts-based)
  - [CouchbaseQueryDocumentStore (GSI-based)](#couchbasequerydocumentstore-gsi-based)
  - [More Examples](#more-examples)
- [License](#license)

## Breaking Changes in Version 2.0.0

> **Important Note:**  
> In version 2.0.0, the following component names have been changed:
>
> - `CouchbaseDocumentStore` is now `CouchbaseSearchDocumentStore`
> - `CouchbaseEmbeddingRetriever` is now `CouchbaseSearchEmbeddingRetriever`
>
> Please update your code accordingly if upgrading from an earlier version.

## Overview

An integration of [Couchbase](https://www.couchbase.com) NoSQL database with [Haystack v2.0](https://docs.haystack.deepset.ai/v2.0/docs/intro)
by [deepset](https://www.deepset.ai). Couchbase supports three types of [vector indexes](https://docs.couchbase.com/server/current/vector-search/vector-search.html) for AI applications, and this library provides document stores for two of them:

### Document Stores

The library provides two document store implementations:

1. **`CouchbaseSearchDocumentStore`** - Uses Couchbase Search Vector Index (FTS-based)
   - Best for: Hybrid searches combining vector, full-text, and geospatial searches
   - Dataset size: Up to ~100 million documents
   - Use case: E-commerce, travel recommendations with complex search requirements

2. **`CouchbaseQueryDocumentStore`** - Uses Couchbase Global Secondary Index (GSI) with vector support
   - Supports both **Hyperscale Vector Index (BHIVE)** and **Composite Vector Index**
   - Best for: Pure vector searches or filtered vector searches at massive scale
   - Dataset size: Tens of millions to billions of documents
   - Use case: Content recommendations, chatbots, anomaly detection, job searches

You can start working with these implementations by importing from the `couchbase_haystack` package:

```python
from couchbase_haystack import CouchbaseSearchDocumentStore, CouchbaseQueryDocumentStore
```

### Retrievers

In addition to the document stores, the library includes the following [retriever components](https://docs.haystack.deepset.ai/v2.0/docs/retrievers):

- **`CouchbaseSearchEmbeddingRetriever`** - Works with `CouchbaseSearchDocumentStore` to perform hybrid searches combining vector similarity with full-text and geospatial queries.

- **`CouchbaseQueryEmbeddingRetriever`** - Works with `CouchbaseQueryDocumentStore` to perform high-performance vector similarity searches using GSI indexes (BHIVE or Composite).

The `couchbase-haystack` library uses the [Couchbase Python SDK](https://docs.couchbase.com/python-sdk/current/hello-world/start-using-sdk.html).

Both document stores store Documents as JSON documents in Couchbase. Embeddings are stored as part of the document, with indexing and querying managed by different Couchbase services depending on the document store type.

## Choosing the Right Document Store

Couchbase supports three types of vector indexes. This library currently supports two of them:

| Feature | CouchbaseSearchDocumentStore (FTS) | CouchbaseQueryDocumentStore (GSI - BHIVE) | CouchbaseQueryDocumentStore (GSI - Composite) |
|---------|-----------------------------------|-------------------------------------------|----------------------------------------------|
| **Index Type** | Search Vector Index | Hyperscale Vector Index (BHIVE) | Composite Vector Index |
| **First Available** | Couchbase 7.6 | Couchbase 8.0 | Couchbase 8.0 |
| **Dataset Size** | Up to ~100 million docs | Tens of millions to billions | Tens of millions to billions |
| **Best For** | Hybrid searches (vector + text + geo) | Pure vector searches at scale | Filtered vector searches |
| **Strengths** | - Full-text search integration<br>- Geospatial search<br>- Familiar FTS indexes | - High performance for pure vector searches<br>- Low memory footprint<br>- Best for huge datasets<br>- Concurrent updates & searches | - Scalar filters before vector search<br>- Efficient for selective queries<br>- Compliance use cases |
| **Use Cases** | - E-commerce product search<br>- Travel recommendations<br>- Real estate searches | - Chatbot context (RAG)<br>- Reverse image search<br>- Anomaly detection | - Content recommendations with filters<br>- Job searches<br>- Supply chain management |
| **Search Type** | Vector + FTS + Geospatial | ANN (Approximate Nearest Neighbor) or KNN | ANN or KNN|
| **Filtering** | Search query filters | SQL++ WHERE clause | SQL++ WHERE clause|

### When to Use Each

- **Use `CouchbaseSearchDocumentStore`** when:
  - You need to combine vector searches with full-text or geospatial searches
  - Your dataset is under 100 million documents
  - You want hybrid search capabilities in a single query

- **Use `CouchbaseQueryDocumentStore` with BHIVE (ANN search)** when:
  - You need pure vector similarity searches at massive scale
  - You want the lowest memory footprint and best performance
  - Your application needs concurrent updates and searches
  - You're building chatbots, recommendation systems, or anomaly detection

- **Use `CouchbaseQueryDocumentStore` with Composite Index** when:
  - You need to apply strict scalar filters before vector search
  - Your queries are highly selective (return small results from large datasets)
  - You have compliance requirements that must exclude certain vectors
  - You're building filtered recommendation or search systems

## Installation

`couchbase-haystack` can be installed as any other Python library, using pip:

```bash
pip install --upgrade pip # optional
pip install sentence-transformers # required in order to run pipeline examples given below
pip install couchbase-haystack
```

## Usage

### Running Couchbase

You will need a running instance of Couchbase to use the components from this package. There are several options available:

- [Docker](https://docs.couchbase.com/server/current/getting-started/do-a-quick-install.html)
- [Couchbase Cloud](https://www.couchbase.com/products/capella) - a fully managed cloud service
- [Couchbase Server](https://www.couchbase.com/downloads) - installable on various operating systems

The simplest way to start the database locally is with a Docker container:

```bash
docker run \
    --restart always \
    --publish=8091-8096:8091-8096 --publish=11210:11210 \
    --env COUCHBASE_ADMINISTRATOR_USERNAME=admin \
    --env COUCHBASE_ADMINISTRATOR_PASSWORD=passw0rd \
    couchbase:enterprise-7.6.2
```

In this example, the container is started using Couchbase Server version `7.6.2`. The `COUCHBASE_ADMINISTRATOR_USERNAME` and `COUCHBASE_ADMINISTRATOR_PASSWORD` environment variables set the default credentials for authentication.

> **Note:**  
> Assuming you have a Docker container running, navigate to <http://localhost:8091> to open the Couchbase Web Console and explore your data.

### CouchbaseSearchDocumentStore (FTS-based)

The `CouchbaseSearchDocumentStore` uses Couchbase's Search Service with FTS (Full-Text Search) vector indexes. It's ideal for hybrid searches that combine vector similarity with full-text and geospatial queries.

```text
                                   +-----------------------------+
                                   |       Couchbase Database    |
                                   +-----------------------------+
                                   |                             |
                                   |      +----------------+     |
                                   |      |  Data service  |     |
                                   write_documents    |      +----------------+     |
          +------------------------+----->|   properties   |     |
          |                        |      |                |     |
+---------+--------------------+   |      |   embedding    |     |
|                              |   |      +--------+-------+     |
| CouchbaseSearchDocumentStore |   |               |             |
|                              |   |               |index        |
+---------+--------------------+   |               |             |
          |                        |      +--------+--------+    |
          |                        |      |  Search service |    |
          |                        |      +-----------------+    |
          +----------------------->|      |       FTS       |    |
               query_embeddings    |      |   Vector Index  |    |
                                   |      | (for embedding) |    |
                                   |      +-----------------+    |
                                   |                             |
                                   +-----------------------------+
```

The document store supports both scope-level and global-level vector search indexes:

- **Scope-level indexes** (default): Created at the scope level, searches only within that scope
- **Global-level indexes**: Created at the bucket level, can search across all scopes and collections

#### Basic Usage

Once you have the package installed and the database running, you can start using `CouchbaseSearchDocumentStore`:

```python
from couchbase_haystack import CouchbaseSearchDocumentStore, CouchbasePasswordAuthenticator
from haystack.utils.auth import Secret

document_store = CouchbaseSearchDocumentStore(
    cluster_connection_string=Secret.from_env_var("CB_CONNECTION_STRING"),
    authenticator=CouchbasePasswordAuthenticator(
      username=Secret.from_env_var("CB_USERNAME"),
      password=Secret.from_env_var("CB_PASSWORD")
    ),
    bucket = "haystack_bucket_name",
    scope="haystack_scope_name",
    collection="haystack_collection_name",
    vector_search_index = "vector_search_index",
    is_global_level_index=False  # Enables scope-level vector search index by default
)
```

Assuming there is a list of documents available and a running couchbase database you can write/index those in Couchbase, e.g.:

```python
from haystack import Document

documents = [Document(content="Alice has been living in New York City for the past 5 years.")]

document_store.write_documents(documents)
```

If you intend to obtain embeddings before writing documents use the following code:

```python
from haystack import Document

# import one of the available document embedders
from haystack.components.embedders import SentenceTransformersDocumentEmbedder 

documents = [Document(content="Alice has been living in New York City for the past 5 years.")]

document_embedder = SentenceTransformersDocumentEmbedder(model="sentence-transformers/all-MiniLM-L6-v2")
document_embedder.warm_up() # will download the model during first run
documents_with_embeddings = document_embedder.run(documents)

document_store.write_documents(documents_with_embeddings.get("documents"))
```

Make sure embedding model produces vectors of same size as it has been set on `Couchbase Vector Index`, e.g. setting `embedding_dim=384` would comply with the "sentence-transformers/all-MiniLM-L6-v2" model.

> **Note**
> Most of the time you will be using [Haystack Pipelines](https://docs.haystack.deepset.ai/v2.0/docs/pipelines) to build both indexing and querying RAG scenarios.

It is important to understand how haystack Documents are stored in Couchbase after you call `write_documents`.

```python
from random import random

sample_embedding = [random() for _ in range(384)]  # using fake/random embedding for brevity here to simplify example
document = Document(
    content="Alice has been living in New York City for the past 5 years.", embedding=sample_embedding, meta={"num_of_years": 5}
)
document.to_dict()
```

The above code converts a Document to a dictionary and will render the following output:

```bash
>>> output:
{
    "id": "11c255ad10bff4286781f596a5afd9ab093ed056d41bca4120c849058e52f24d",
    "content": "Alice has been living in New York City for the past 5 years.",
    "dataframe": None,
    "blob": None,
    "score": None,
    "embedding": [0.025010755222666936, 0.27502931836911926, 0.22321073814882275, ...], # vector of size 384
    "num_of_years": 5,
}
```

The data from the dictionary will be used to create a document in Couchbase after you write the document with `document_store.write_documents([document])`. You could query it with Cypher, e.g. `MATCH (doc:Document) RETURN doc`. Below is a json document Couchbase:

```js
{
  "id": "11c255ad10bff4286781f596a5afd9ab093ed056d41bca4120c849058e52f24d",
  "embedding": [0.6394268274307251, 0.02501075528562069,0.27502933144569397, ...], // vector of size 384
  "content": "Alice has been living in New York City for the past 5 years.",
  "meta": {
    "num_of_years": 5
  }
}
```

The full list of parameters accepted by `CouchbaseSearchDocumentStore` can be found in
[API documentation](https://couchbase-ecosystem.github.io/couchbase-haystack/reference/couchbase_document_store).

#### Indexing Documents with CouchbaseSearchDocumentStore

With Haystack you can use [DocumentWriter](https://docs.haystack.deepset.ai/v2.0/docs/documentwriter) component to write Documents into a Document Store. In the example below we construct pipeline to write documents to Couchbase using `CouchbaseSearchDocumentStore`:

```python
from haystack import Document
from haystack.components.embedders import SentenceTransformersDocumentEmbedder
from haystack.components.writers import DocumentWriter
from haystack.pipeline import Pipeline
from haystack.utils.auth import Secret

from couchbase_haystack import CouchbaseSearchDocumentStore, CouchbasePasswordAuthenticator

documents = [Document(content="This is document 1"), Document(content="This is document 2")]

document_store = CouchbaseSearchDocumentStore(
    cluster_connection_string=Secret.from_env_var("CB_CONNECTION_STRING"),
    authenticator=CouchbasePasswordAuthenticator(
      username=Secret.from_env_var("CB_USERNAME"),
      password=Secret.from_env_var("CB_PASSWORD")
    ),
    bucket = "haystack_bucket_name",
    scope="haystack_scope_name",
    collection="haystack_collection_name",
    vector_search_index = "vector_search_index"
)
embedder = SentenceTransformersDocumentEmbedder(model="sentence-transformers/all-MiniLM-L6-v2")
document_writer = DocumentWriter(document_store=document_store)

indexing_pipeline = Pipeline()
indexing_pipeline.add_component(instance=embedder, name="embedder")
indexing_pipeline.add_component(instance=document_writer, name="writer")

indexing_pipeline.connect("embedder", "writer")
indexing_pipeline.run({"embedder": {"documents": documents}})
```

```bash
>>> output:
`{'writer': {'documents_written': 2}}`
```

#### Retrieving Documents with CouchbaseSearchEmbeddingRetriever

`CouchbaseSearchEmbeddingRetriever` component can be used to retrieve documents from Couchbase by querying the FTS vector index using an embedded query. Below is a pipeline which finds documents using query embedding:

```python
from typing import List
from haystack.utils.auth import Secret
from haystack import Document, Pipeline
from haystack.components.embedders import SentenceTransformersDocumentEmbedder, SentenceTransformersTextEmbedder

from couchbase_haystack.document_store import CouchbaseSearchDocumentStore, CouchbasePasswordAuthenticator
from couchbase_haystack.component.retriever import CouchbaseSearchEmbeddingRetriever

document_store = CouchbaseSearchDocumentStore(
    cluster_connection_string=Secret.from_env_var("CB_CONNECTION_STRING"),
    authenticator=CouchbasePasswordAuthenticator(
      username=Secret.from_env_var("CB_USERNAME"),
      password=Secret.from_env_var("CB_PASSWORD")
    ),
    bucket = "haystack_bucket_name",
    scope="haystack_scope_name",
    collection="haystack_collection_name",
    vector_search_index = "vector_search_index"
)

documents = [
    Document(content="Alice has been living in New York City for the past 5 years.", meta={"num_of_years": 5, "city": "New York"}),
    Document(content="John moved to Los Angeles 2 years ago and loves the sunny weather.", meta={"num_of_years": 2, "city": "Los Angeles"}),
]

# Same model is used for both query and Document embeddings
model_name = "sentence-transformers/all-MiniLM-L6-v2"

document_embedder = SentenceTransformersDocumentEmbedder(model=model_name)
document_embedder.warm_up()
documents_with_embeddings = document_embedder.run(documents)

document_store.write_documents(documents_with_embeddings.get("documents"))

print("Number of documents written: ", document_store.count_documents())

pipeline = Pipeline()
pipeline.add_component("text_embedder", SentenceTransformersTextEmbedder(model=model_name))
pipeline.add_component("retriever", CouchbaseSearchEmbeddingRetriever(document_store=document_store))
pipeline.connect("text_embedder.embedding", "retriever.query_embedding")

result = pipeline.run(
    data={
        "text_embedder": {"text": "What cities do people live in?"},
        "retriever": {
            "top_k": 5
        },
    }
)

documents: List[Document] = result["retriever"]["documents"]
```

```bash
>>> output:
[Document(id=3e35fa03aff6e3c45e6560f58adc4fde3c436c111a8809c30133b5cb492e8694, content: 'Alice has been living in New York City for the past 5 years.', meta: {'num_of_years': 5, 'city': 'New York'}, score: 0.36796408891677856, embedding: "embedding": vector of size 384), Document(id=ca4d7d7d7ff6c13b950a88580ab134b2dc15b48a47b8f571a46b354b5344e5fa, content: 'John moved to Los Angeles 2 years ago and loves the sunny weather.', meta: {'num_of_years': 2, 'city': 'Los Angeles'}, score: 0.3126790523529053, embedding: vector of size 384)]
```

---

### CouchbaseQueryDocumentStore (GSI-based)

The `CouchbaseQueryDocumentStore` uses Couchbase's Global Secondary Index (GSI) with vector support. It's designed for high-performance vector searches at massive scale using SQL++ queries.

```text
                                   +-----------------------------+
                                   |       Couchbase Database    |
                                   +-----------------------------+
                                   |                             |
                                   |      +----------------+     |
                                   |      |  Data service  |     |
                                   write_documents    |      +----------------+     |
          +------------------------+----->|   properties   |     |
          |                        |      |                |     |
+---------+--------------------+   |      |   embedding    |     |
|                              |   |      +--------+-------+     |
| CouchbaseQueryDocumentStore  |   |               |             |
|                              |   |               |index        |
+---------+--------------------+   |               |             |
          |                        |      +--------+--------+    |
          |                        |      |  Index service  |    |
          |                        |      +-----------------+    |
          +----------------------->|      |       GSI       |    |
               query_embeddings    |      |  BHIVE/Composite|    |
                                   |      | (for embedding) |    |
                                   |      +-----------------+    |
                                   |                             |
                                   +-----------------------------+
```

#### Key Features

- **Two Index Types Supported:**
  - **Hyperscale Vector Index (BHIVE)**: Optimized for pure vector searches, scales to billions of documents
  - **Composite Vector Index**: Combines scalar and vector indexing for filtered searches

- **Search Types:**
  - **ANN (Approximate Nearest Neighbor)**: Fast approximate search using `APPROX_VECTOR_DISTANCE()`
  - **KNN (K-Nearest Neighbors)**: Exact search using `VECTOR_DISTANCE()`

- **Similarity Metrics:**
  - `COSINE` - Cosine similarity
  - `DOT` - Dot product similarity  
  - `L2` / `EUCLIDEAN` - Euclidean distance
  - `L2_SQUARED` / `EUCLIDEAN_SQUARED` - Squared Euclidean distance

#### Basic Usage

```python
from couchbase_haystack import CouchbaseQueryDocumentStore, CouchbasePasswordAuthenticator, QueryVectorSearchType, CouchbaseQueryOptions
from haystack.utils.auth import Secret
from couchbase.n1ql import QueryScanConsistency
from datetime import timedelta

# Example 1: Using BHIVE (Hyperscale Vector Index) for pure vector search
document_store_bhive = CouchbaseQueryDocumentStore(
    cluster_connection_string=Secret.from_env_var("CB_CONNECTION_STRING"),
    authenticator=CouchbasePasswordAuthenticator(
        username=Secret.from_env_var("CB_USERNAME"),
        password=Secret.from_env_var("CB_PASSWORD")
    ),
    bucket="haystack_bucket_name",
    scope="haystack_scope_name",
    collection="haystack_collection_name",
    search_type=QueryVectorSearchType.ANN,  # or QueryVectorSearchType.KNN
    similarity=QueryVectorSearchSimilarity.COSINE,  # or "DOT", "L2", "EUCLIDEAN", "L2_SQUARED", "EUCLIDEAN_SQUARED"
    nprobes=10,  # Number of probes for ANN search (optional)
    query_options=CouchbaseQueryOptions(
        timeout=timedelta(seconds=60),
        scan_consistency=QueryScanConsistency.NOT_BOUNDED
    )
)

# Example 2: Using Composite Vector Index for filtered searches
document_store_composite = CouchbaseQueryDocumentStore(
    cluster_connection_string=Secret.from_env_var("CB_CONNECTION_STRING"),
    authenticator=CouchbasePasswordAuthenticator(
        username=Secret.from_env_var("CB_USERNAME"),
        password=Secret.from_env_var("CB_PASSWORD")
    ),
    bucket="haystack_bucket_name",
    scope="haystack_scope_name",
    collection="haystack_collection_name",
    search_type=QueryVectorSearchType.ANN,
    similarity=QueryVectorSearchSimilarity.COSINE,
    nprobes=10
)
```

> **Note:** You need to create the appropriate GSI index manually in Couchbase before performing vector search. See the [Couchbase documentation](https://docs.couchbase.com/server/current/n1ql/n1ql-language-reference/createindex.html) for index creation details.

#### Indexing Documents with CouchbaseQueryDocumentStore

```python
from haystack import Document
from haystack.components.embedders import SentenceTransformersDocumentEmbedder
from haystack.components.writers import DocumentWriter
from haystack.pipeline import Pipeline
from haystack.utils.auth import Secret

from couchbase_haystack import CouchbaseQueryDocumentStore, CouchbasePasswordAuthenticator, QueryVectorSearchType

documents = [
    Document(content="Machine learning is transforming healthcare.", meta={"category": "technology"}),
    Document(content="Deep learning models require large datasets.", meta={"category": "AI"})
]

document_store = CouchbaseQueryDocumentStore(
    cluster_connection_string=Secret.from_env_var("CB_CONNECTION_STRING"),
    authenticator=CouchbasePasswordAuthenticator(
        username=Secret.from_env_var("CB_USERNAME"),
        password=Secret.from_env_var("CB_PASSWORD")
    ),
    bucket="haystack_bucket_name",
    scope="haystack_scope_name",
    collection="haystack_collection_name",
    search_type=QueryVectorSearchType.ANN,
    similarity=QueryVectorSearchSimilarity.COSINE
)

embedder = SentenceTransformersDocumentEmbedder(model="sentence-transformers/all-MiniLM-L6-v2")
document_writer = DocumentWriter(document_store=document_store)

indexing_pipeline = Pipeline()
indexing_pipeline.add_component(instance=embedder, name="embedder")
indexing_pipeline.add_component(instance=document_writer, name="writer")

indexing_pipeline.connect("embedder", "writer")
result = indexing_pipeline.run({"embedder": {"documents": documents}})
print(result)  # {'writer': {'documents_written': 2}}
```

#### Retrieving Documents with CouchbaseQueryEmbeddingRetriever

The `CouchbaseQueryEmbeddingRetriever` uses SQL++ queries with vector functions to retrieve similar documents efficiently:

```python
from typing import List
from haystack import Document, Pipeline
from haystack.components.embedders import SentenceTransformersDocumentEmbedder, SentenceTransformersTextEmbedder
from haystack.utils.auth import Secret

from couchbase_haystack import CouchbaseQueryDocumentStore, CouchbaseQueryEmbeddingRetriever, CouchbasePasswordAuthenticator, QueryVectorSearchType

# Initialize document store
document_store = CouchbaseQueryDocumentStore(
    cluster_connection_string=Secret.from_env_var("CB_CONNECTION_STRING"),
    authenticator=CouchbasePasswordAuthenticator(
        username=Secret.from_env_var("CB_USERNAME"),
        password=Secret.from_env_var("CB_PASSWORD")
    ),
    bucket="haystack_bucket_name",
    scope="haystack_scope_name",
    collection="haystack_collection_name",
    search_type=QueryVectorSearchType.ANN,
    similarity=QueryVectorSearchSimilarity.COSINE,
    nprobes=10
)

# Create and embed documents
documents = [
    Document(content="Python is a popular programming language.", meta={"category": "programming", "year": 2024}),
    Document(content="JavaScript is widely used for web development.", meta={"category": "programming", "year": 2024}),
    Document(content="Machine learning is a subset of AI.", meta={"category": "AI", "year": 2023}),
]

model_name = "sentence-transformers/all-MiniLM-L6-v2"
document_embedder = SentenceTransformersDocumentEmbedder(model=model_name)
document_embedder.warm_up()
documents_with_embeddings = document_embedder.run(documents)

document_store.write_documents(documents_with_embeddings.get("documents"))

# Create retrieval pipeline
pipeline = Pipeline()
pipeline.add_component("text_embedder", SentenceTransformersTextEmbedder(model=model_name))
pipeline.add_component("retriever", CouchbaseQueryEmbeddingRetriever(document_store=document_store, top_k=5))
pipeline.connect("text_embedder.embedding", "retriever.query_embedding")

# Example 1: Basic retrieval without filters
result = pipeline.run(
    data={
        "text_embedder": {"text": "What is Python used for?"},
        "retriever": {"top_k": 3}
    }
)

documents: List[Document] = result["retriever"]["documents"]
print(f"Found {len(documents)} documents")
for doc in documents:
    print(f"  - {doc.content} (score: {doc.score})")

# Example 2: Retrieval with filters (applies WHERE clause before vector search)
result_filtered = pipeline.run(
    data={
        "text_embedder": {"text": "Tell me about programming languages"},
        "retriever": {
            "top_k": 3,
            "filters": {"field": "meta.category", "operator": "==", "value": "programming"}
        }
    }
)

print(f"\nFiltered results: {len(result_filtered['retriever']['documents'])} documents")

# Example 3: Custom nprobes for this query
result_custom = pipeline.run(
    data={
        "text_embedder": {"text": "artificial intelligence"},
        "retriever": {
            "top_k": 2,
            "nprobes": 20  # Override the document store's nprobes setting
        }
    }
)
```

#### Understanding Search Types and Parameters

**ANN (Approximate Nearest Neighbor) vs KNN:**

- **ANN**: Uses `APPROX_VECTOR_DISTANCE()` - faster, suitable for large datasets, may have slight accuracy trade-off
- **KNN**: Uses `VECTOR_DISTANCE()` - exact search, slower on very large datasets, guaranteed accuracy

**nprobes Parameter:**

- Only applies to ANN searches
- Higher values = more accurate but slower
- Lower values = faster but potentially less accurate
- Can be set at document store level or per query
- Typical range: 1-50 (default depends on index configuration)

**Similarity Metrics:**

- `COSINE`: Range [-1, 1], normalized, good for text embeddings
- `DOT`: Unnormalized, good for normalized vectors
- `L2` / `EUCLIDEAN`: Euclidean distance, lower is better
- `L2_SQUARED` / `EUCLIDEAN_SQUARED`: Squared Euclidean distance, lower is better

### More Examples

You can find more examples in the [examples](examples) directory:

#### Search-based (FTS) Examples

- [examples/search/indexing_pipeline.py](examples/search/indexing_pipeline.py) - Indexing documents using `CouchbaseSearchDocumentStore`
- [examples/search/rag_pipeline.py](examples/search/rag_pipeline.py) - RAG pipeline using `CouchbaseSearchEmbeddingRetriever` with [HuggingFaceAPIGenerator](https://docs.haystack.deepset.ai/v2.0/docs/huggingfacetgigenerator)

#### GSI-based Examples

- [examples/gsi/indexing_pipeline.py](examples/gsi/indexing_pipeline.py) - Indexing documents using `CouchbaseQueryDocumentStore` with BHIVE or Composite indexes
- [examples/gsi/rag_pipeline.py](examples/gsi/rag_pipeline.py) - RAG pipeline using `CouchbaseQueryEmbeddingRetriever` for high-performance vector retrieval

## License

`couchbase-haystack` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license
---

## 📢 Support Policy

We truly appreciate your interest in this project!  
This project is **community-maintained**, which means it's **not officially supported** by our support team.

If you need help, have found a bug, or want to contribute improvements, the best place to do that is right here — by [opening a GitHub issue](https://github.com/Couchbase-Ecosystem/couchbase-haystack/issues).  
Our support portal is unable to assist with requests related to this project, so we kindly ask that all inquiries stay within GitHub.

Your collaboration helps us all move forward together — thank you!
