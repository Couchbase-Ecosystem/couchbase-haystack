---
id: overview
title: Overview
slug: /
---

# Couchbase Haystack Integration

A [Haystack](https://docs.haystack.deepset.ai/docs/document_store) Document Store for [Couchbase](https://www.couchbase.com).

[![ci](https://github.com/Couchbase-Ecosystem/couchbase-haystack/workflows/ci/badge.svg)](https://github.com/Couchbase-Ecosystem/couchbase-haystack/actions?query=workflow%3Aci)
[![pypi version](https://img.shields.io/pypi/v/couchbase-haystack.svg)](https://pypi.org/project/couchbase-haystack/)
[![haystack version](https://img.shields.io/pypi/v/haystack-ai.svg?label=haystack)](https://pypi.org/project/haystack-ai/)

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

An integration of [Couchbase](https://www.couchbase.com) NoSQL database with [Haystack v2.0](https://docs.haystack.deepset.ai/v2.0/docs/intro) by [deepset](https://www.deepset.ai). In Couchbase [Vector search index](https://docs.couchbase.com/server/current/vector-search/vector-search.html) is being used for indexing document embeddings and dense retrievals.

The library allows using Couchbase as a [DocumentStore](https://docs.haystack.deepset.ai/v2.0/docs/document-store), and implements the required [Protocol](https://docs.haystack.deepset.ai/v2.0/docs/document-store#documentstore-protocol) methods. You can start working with the implementation by importing it from `couchbase_haystack` package:

```python
from couchbase_haystack import CouchbaseDocumentStore
```

In addition to the `CouchbaseDocumentStore`, the library includes the following Haystack components which can be used in a pipeline:

- **CouchbaseEmbeddingRetriever**: A typical [retriever component](https://docs.haystack.deepset.ai/v2.0/docs/retrievers) which can be used to query the vector store index and find related Documents. The component uses `CouchbaseDocumentStore` to query embeddings.

The `couchbase-haystack` library uses [Python Driver](https://docs.couchbase.com/python-sdk/current/hello-world/start-using-sdk.html).

`CouchbaseDocumentStore` will store Documents as JSON documents in Couchbase. Embeddings are stored as part of the document, with indexing and querying of vector embeddings managed by Couchbase's dedicated [Vector Search Index](https://docs.couchbase.com/server/current/vector-search/vector-search.html).

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
+---------+--------------+         |      |   embedding    |     |
|                        |         |      +--------+-------+     |
| CouchbaseDocumentStore |         |               |             |
|                        |         |               |index        |
+---------+--------------+         |               |             |
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

In the above diagram:

- **Data service**: Supports the storing, setting, and retrieving of documents, specified by key. Basically where the documents are stored in key value.
- **Properties**: Are Document [attributes](https://docs.haystack.deepset.ai/v2.0/docs/data-classes#document) stored as part of the Document.
- **Embedding**: Is also a property of the Document (just shown separately in the diagram for clarity) which is a vector of type `LIST[FLOAT]`.
- **Search service**: Where indexes specially purposed for Full Text Search and Vector search are created. The Search Service allows for efficient querying and retrieval based on both text content and vector embeddings.

`CouchbaseDocumentStore` requires the vector index to be created manually either by SDK or UI. Before writing documents, you should make sure Documents are embedded by one of the provided [embedders](https://docs.haystack.deepset.ai/v2.0/docs/embedders). For example, [SentenceTransformersDocumentEmbedder](https://docs.haystack.deepset.ai/v2.0/docs/sentencetransformersdocumentembedder) can be used in the indexing pipeline to calculate document embeddings before writing those to Couchbase.

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
> Assuming you have a Docker container running, navigate to http://localhost:8091 to open the Couchbase Web Console and explore your data.

### Document Store

Once you have the package installed and the database running, you can start using `CouchbaseDocumentStore` as any other document stores that support embeddings.

```python
from couchbase_haystack import CouchbaseDocumentStore

document_store = CouchbaseDocumentStore(
    cluster_connection_string= Secret.from_token("localhost"),
    authenticator=CouchbasePasswordAuthenticator(
        username = Secret.from_token("username"),
        password = Secret.from_token("password")
    ),
    bucket = "haystack_bucket_name",
    scope="haystack_scope_name",
    collection="haystack_collection_name",
    vector_search_index = "vector_search_index"
)
```

Assuming there is a list of documents available and a running Couchbase database, you can write/index those in Couchbase, e.g.:

```python
from haystack import Document

documents = [Document(content="My name is Morgan and I live in Paris.")]

document_store.write_documents(documents)
```

If you intend to obtain embeddings before writing documents, use the following code:

```python
from haystack import Document

# import one of the available document embedders
from haystack.components.embedders import SentenceTransformersDocumentEmbedder 

documents = [Document(content="My name is Morgan and I live in Paris.")]

document_embedder = SentenceTransformersDocumentEmbedder(model="sentence-transformers/all-MiniLM-L6-v2")
document_embedder.warm_up() # will download the model during first run
documents_with_embeddings = document_embedder.run(documents)

document_store.write_documents(documents_with_embeddings.get("documents"))
```

Make sure the embedding model produces vectors of the same size as it has been set on `Couchbase Vector Index`, e.g., setting `embedding_dim=384` would comply with the "sentence-transformers/all-MiniLM-L6-v2" model.

> **Note**
> Most of the time you will be using [Haystack Pipelines](https://docs.haystack.deepset.ai/v2.0/docs/pipelines) to build both indexing and querying RAG scenarios.

It is important to understand how Haystack Documents are stored in Couchbase after you call `write_documents`.

```python
from random import random

sample_embedding = [random() for _ in range(384)]  # using fake/random embedding for brevity here to simplify example
document = Document(
    content="My name is Morgan and I live in Paris.", embedding=sample_embedding, meta={"num_of_years": 3}
)
document.to_dict()
```

The above code converts a Document to a dictionary and will render the following output:

```bash
>>> output:
{
    "id": "11c255ad10bff4286781f596a5afd9ab093ed056d41bca4120

c849058e52f24d",
    "content": "My name is Morgan and I live in Paris.",
    "dataframe": None,
    "blob": None,
    "score": None,
    "embedding": [0.025010755222666936, 0.27502931836911926, 0.22321073814882275, ...], # vector of size 384
    "num_of_years": 3,
}
```

The data from the dictionary will be used to create a document in Couchbase after you write the document with `document_store.write_documents([document])`. You could query it with Cypher, e.g., `MATCH (doc:Document) RETURN doc`. Below is a JSON document Couchbase:

```js
{
  "id": "11c255ad10bff4286781f596a5afd9ab093ed056d41bca4120c849058e52f24d",
  "embedding": [0.6394268274307251, 0.02501075528562069,0.27502933144569397, ...], // vector of size 384
  "content": "My name is Morgan and I live in Paris.",
  "meta": {
    "num_of_years": 3
  }
}
```

The full list of parameters accepted by `CouchbaseDocumentStore` can be found in [API documentation](test.com).

### Indexing Documents

With Haystack you can use [DocumentWriter](https://docs.haystack.deepset.ai/v2.0/docs/documentwriter) component to write Documents into a Document Store. In the example below, we construct a pipeline to write documents to Couchbase using `CouchbaseDocumentStore`:

```python
from haystack import Document
from haystack.components.embedders import SentenceTransformersDocumentEmbedder
from haystack.components.writers import DocumentWriter
from haystack.pipeline import Pipeline

from couchbase_haystack import CouchbaseDocumentStore, CouchbasePasswordAuthenticator

documents = [Document(content="This is document 1"), Document(content="This is document 2")]

document_store = CouchbaseDocumentStore(
    cluster_connection_string= Secret.from_token("localhost"),
    authenticator=CouchbasePasswordAuthenticator(
        username = Secret.from_token("username"),
        password = Secret.from_token("password")
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

### Retrieving Documents

`CouchbaseEmbeddingRetriever` component can be used to retrieve documents from Couchbase by querying vector index using an embedded query. Below is a pipeline which finds documents using query embedding:

```python
from typing import List

from haystack import Document, Pipeline
from haystack.components.embedders import SentenceTransformersDocumentEmbedder, SentenceTransformersTextEmbedder

from couchbase_haystack.document_store import CouchbaseDocumentStore, CouchbasePasswordAuthenticator
from couchbase_haystack.component.retriever import CouchbaseEmbeddingRetriever

document_store = CouchbaseDocumentStore(
    cluster_connection_string= Secret.from_token("localhost"),
    authenticator=CouchbasePasswordAuthenticator(
        username = Secret.from_token("username"),
        password = Secret.from_token("password")
    ),
    bucket = "haystack_bucket_name",
    scope="haystack_scope_name",
    collection="haystack_collection_name",
    vector_search_index = "vector_search_index"
)

documents = [
    Document(content="My name is Morgan and I live in Paris.", meta={"num_of_years": 3}),
    Document(content="I am Susan and I live in Berlin.", meta={"num_of_years": 7}),
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
pipeline.add_component("retriever", CouchbaseEmbeddingRetriever(document_store=document_store))
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
[Document(id=3930326edabe6d172031557556999e2f8ba258ccde3c876f5e3ac7e66ed3d53a, content: 'My name is Morgan and I live in Paris.', meta: {'num_of_years': 3}, score: 0.8348373770713806)]
```

### More Examples

You can find more examples in the implementation [repository](examples):

- [indexing_pipeline.py](https://github.com/Couchbase-Ecosystem/couchbase-haystack/examples/indexing_pipeline.py) - Indexing text files (documents) from a remote HTTP location.
- [rag_pipeline.py](https://github.com/Couchbase-Ecosystem/couchbase-haystack/examples/rag_pipeline.py) - Generative question answering RAG pipeline using `CouchbaseEmbeddingRetriever` to fetch documents from Couchbase document store and answer questions using [HuggingFaceTGIGenerator](https://docs.haystack.deepset.ai/v2.0/docs/huggingfacetgigenerator).

## License

`couchbase-haystack` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.