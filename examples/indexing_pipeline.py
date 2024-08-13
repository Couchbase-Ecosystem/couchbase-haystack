import logging
import os
import zipfile
from io import BytesIO
from pathlib import Path

from haystack.utils import Secret

import requests
from haystack import Pipeline
from haystack.components.converters import TextFileToDocument
from haystack.components.embedders import SentenceTransformersDocumentEmbedder
from haystack.components.preprocessors import DocumentCleaner, DocumentSplitter
from haystack.components.writers import DocumentWriter

from couchbase_haystack import CouchbaseDocumentStore, CouchbasePasswordAuthenticator
      



logger = logging.getLogger(__name__)


def fetch_archive_from_http(url: str, output_dir: str):
    if Path(output_dir).is_dir():
        logger.warn(f"'{output_dir}' directory already exists. Skipping data download")
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
#     couchbase:enterprise-7.6.2

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

# Create components and an indexing pipeline that converts txt to documents, cleans and splits them, and
# indexes them for dense retrieval.
p = Pipeline()
p.add_component("text_file_converter", TextFileToDocument())
p.add_component("cleaner", DocumentCleaner())
p.add_component("splitter", DocumentSplitter(split_by="sentence", split_length=250, split_overlap=30))
p.add_component("embedder", SentenceTransformersDocumentEmbedder(model="sentence-transformers/all-MiniLM-L6-v2"))
p.add_component("writer", DocumentWriter(document_store=document_store))

p.connect("text_file_converter.documents", "cleaner.documents")
p.connect("cleaner.documents", "splitter.documents")
p.connect("splitter.documents", "embedder.documents")
p.connect("embedder.documents", "writer.documents")

# Take the docs data directory as input and run the pipeline
file_paths = [docs_dir / Path(name) for name in os.listdir(docs_dir)]
result = p.run({"text_file_converter": {"sources": file_paths}})

# Assuming you have a Docker container running, navigate to <http://localhost:8091> to open the Couchbase Web Console and explore your data.