# SPDX-FileCopyrightText: 2023-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0
"""
Couchbase integration for Haystack.

This package provides components to use Couchbase as a document store and retriever in Haystack pipelines.
It includes authentication methods, document store implementation, and embedding-based retrieval functionality.
"""

from couchbase_haystack.components.retrievers import CouchbaseSearchEmbeddingRetriever
from couchbase_haystack.document_stores import (
    CouchbaseAuthenticator,
    CouchbaseCertificateAuthenticator,
    CouchbaseClusterOptions,
    CouchbasePasswordAuthenticator,
    CouchbaseSearchDocumentStore,
)

__all__ = [
    "CouchbaseAuthenticator",
    "CouchbaseCertificateAuthenticator",
    "CouchbaseClusterOptions",
    "CouchbasePasswordAuthenticator",
    "CouchbaseSearchDocumentStore",
    "CouchbaseSearchEmbeddingRetriever",
]
