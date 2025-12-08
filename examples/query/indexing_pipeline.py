import json
import logging
import os
import zipfile
from datetime import timedelta
from io import BytesIO
from pathlib import Path

import requests
from couchbase.n1ql import QueryScanConsistency
from haystack import Pipeline
from haystack.components.converters import TextFileToDocument
from haystack.components.embedders import SentenceTransformersDocumentEmbedder
from haystack.components.preprocessors import DocumentCleaner, DocumentSplitter
from haystack.components.writers import DocumentWriter
from haystack.utils import Secret

from couchbase_haystack import (
    CouchbasePasswordAuthenticator,
    CouchbaseQueryDocumentStore,
    CouchbaseQueryOptions,
    QueryVectorSearchType,
    CouchbaseClusterOptions,
)
from couchbase.options import KnownConfigProfiles, QueryOptions

logger = logging.getLogger(__name__)


def fetch_archive_from_http(url: str, output_dir: str):
    if Path(output_dir).is_dir():
        logger.warning(f"'{output_dir}' directory already exists. Skipping data download")
        return

    with requests.get(url, timeout=10, stream=True) as response:
        with zipfile.ZipFile(BytesIO(response.content)) as zip_ref:
            zip_ref.extractall(output_dir)


# Let's first get some files that we want to use
docs_dir = "data/docs"
fetch_archive_from_http(
    url="https://s3.eu-central-1.amazonaws.com/deepset.ai-farm-qa/datasets/documents/wiki_gameofthrones_txt6.zip",
    output_dir=docs_dir,
)

# Make sure you have a running couchbase database, e.g. with Docker:
# docker run \
#     --restart always \
#     --publish=8091-8096:8091-8096 --publish=11210:11210 \
#     --env COUCHBASE_ADMINISTRATOR_USERNAME=admin \
#     --env COUCHBASE_ADMINISTRATOR_PASSWORD=passw0rd \
#     couchbase:enterprise-8.0.0

bucket_name = os.getenv("BUCKET_NAME")
scope_name = os.getenv("SCOPE_NAME")
collection_name = os.getenv("COLLECTION_NAME")
index_name = os.getenv("INDEX_NAME")

document_store = CouchbaseQueryDocumentStore(
    cluster_connection_string=Secret.from_env_var("CONNECTION_STRING"),
    authenticator=CouchbasePasswordAuthenticator(username=Secret.from_env_var("USER_NAME"), password=Secret.from_env_var("PASSWORD")),
    cluster_options=CouchbaseClusterOptions(profile=KnownConfigProfiles.WanDevelopment),
    bucket=bucket_name,
    scope=scope_name,
    collection=collection_name,
    search_type=QueryVectorSearchType.ANN,
    similarity="L2",
    nprobes=10,
    query_options=CouchbaseQueryOptions(timeout=timedelta(seconds=300), scan_consistency=QueryScanConsistency.REQUEST_PLUS),
)


# Create components and an indexing pipeline that converts txt to documents, cleans and splits them, and
# indexes them for dense retrieval.
p = Pipeline()
p.add_component("text_file_converter", TextFileToDocument())
p.add_component("cleaner", DocumentCleaner())
p.add_component("splitter", DocumentSplitter(split_by="word", split_length=250, split_overlap=30))
p.add_component("embedder", SentenceTransformersDocumentEmbedder(model="sentence-transformers/all-MiniLM-L6-v2"))
p.add_component("writer", DocumentWriter(document_store=document_store))

p.connect("text_file_converter.documents", "cleaner.documents")
p.connect("cleaner.documents", "splitter.documents")
p.connect("splitter.documents", "embedder.documents")
p.connect("embedder.documents", "writer.documents")

# Take the docs data directory as input and run the pipeline
file_paths = [docs_dir / Path(name) for name in os.listdir(docs_dir)]
result = p.run({"text_file_converter": {"sources": file_paths}})

logger.info(f"Data written to Couchbase: {result}")

# Assuming you have a Docker container running, navigate to <http://localhost:8091>
# to open the Couchbase Web Console and explore your data.


# currently index needs to be created after some documents are available in the collection for training
# this is a current limitation of the couchbase gsi vector index
cfg = {
    "dimension": 384,
    "description": "IVF,PQ32x8",
    "similarity": "L2",
}
document_store.scope.query(f"Create Index {index_name} ON {collection_name} (embedding vector) USING GSI WITH {json.dumps(cfg)}", QueryOptions(timeout=timedelta(seconds=300))).execute()

logger.info(f"Index created: {index_name}")