# SPDX-FileCopyrightText: 2023-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0
import os
import pytest
from datetime import datetime
from typing import List

from haystack.dataclasses import Document
from haystack.document_stores.types import DuplicatePolicy
from haystack.utils.auth import Secret
from couchbase_haystack import (
    CouchbaseGSIDocumentStore,
    IndexParams,
    IndexType,
    VectorSimilarityMetric
)
from couchbase_haystack.document_stores.auth import CouchbasePasswordAuthenticator
from couchbase_haystack.document_stores.cluster_options import CouchbaseClusterOptions
from couchbase.options import KnownConfigProfiles

# Test configuration
TEST_BUCKET = "test"
TEST_SCOPE = "test_scope"
TEST_COLLECTION = "test_collection"
TEST_INDEX = "test_vector_index"
VECTOR_DIMENSION = 1536

@pytest.fixture(scope="module")
def sample_init_documents() -> List[Document]:
    """Create sample documents for testing."""
    return [
        Document(
            id=f"doc_init_{i}",
            content=f"Test document {i}",
            meta={
                "field1": f"value{i}",
                "field2": i,
                "created_at": datetime.now().isoformat()
            },
            embedding=[0.9 * i] * VECTOR_DIMENSION
        )
        for i in range(1024)
    ]

@pytest.fixture(scope="module")
def document_store(sample_init_documents):
    """Create a document store instance for integration testing."""
    # Create authenticator
    authenticator = CouchbasePasswordAuthenticator(
        username=Secret.from_env_var("USER_NAME"),
        password=Secret.from_env_var("PASSWORD")
    )
    
    # Create cluster options
    cluster_options = CouchbaseClusterOptions(
        protocol=KnownConfigProfiles.WanDevelopment
    )
    
    # Create index parameters
    index_params = IndexParams(
        dimension=VECTOR_DIMENSION,
        similarity=VectorSimilarityMetric.COSINE,
        description="IVF256,SQ8",
        kwargs={"train_list": 256}
    )
    
    # Create document store
    store = CouchbaseGSIDocumentStore(
        cluster_connection_string=Secret.from_env_var("CONNECTION_STRING"),
        authenticator=authenticator,
        cluster_options=cluster_options,
        bucket=TEST_BUCKET,
        scope=TEST_SCOPE,
        collection=TEST_COLLECTION,
        index_name=TEST_INDEX,
        index_type=IndexType.COMPOSITE,
        vector_field="embedding",
        index_params=index_params
    )

    # Write initial documents
    store.write_documents(sample_init_documents, policy=DuplicatePolicy.OVERWRITE)
    
    # Create index before tests
    store.create_index()
    store.delete_documents([doc.id for doc in store.filter_documents()])
    
    yield store
    # Cleanup after tests
    store.collection.query_indexes().drop_index(TEST_INDEX)


@pytest.fixture
def sample_documents() -> List[Document]:
    """Create sample documents for testing."""
    return [
        Document(
            id=f"doc_{i}",
            content=f"Test document {i}",
            meta={
                "field1": f"value{i}",
                "field2": i,
                "created_at": datetime.now().isoformat()
            },
            embedding=[0.1 * i] * VECTOR_DIMENSION
        )
        for i in range(1024)
    ]

def test_write_and_read_documents(document_store, sample_documents):
    """Test writing and reading documents."""
    # Write documents
    written_count = document_store.write_documents(sample_documents, policy=DuplicatePolicy.OVERWRITE)
    assert written_count == len(sample_documents)
    
    # Read documents using filter
    documents = document_store.filter_documents()
    assert len(documents) == len(sample_documents)
    
    # Verify document contents
    for doc in documents:
        assert doc.id.startswith("doc_")
        assert doc.content.startswith("Test document")
        assert "field1" in doc.meta
        assert "field2" in doc.meta
        assert "created_at" in doc.meta
        assert len(doc.embedding) == VECTOR_DIMENSION

def test_duplicate_document_handling(document_store, sample_documents):
    """Test handling of duplicate documents."""
    # Write documents first time
    document_store.write_documents(sample_documents)
    
    # Try to write same documents again with FAIL policy
    with pytest.raises(Exception):
        document_store.write_documents(sample_documents)
    
    # Write with OVERWRITE policy
    document_store.write_documents(sample_documents, policy=DuplicatePolicy.OVERWRITE)
    
    # Verify document count hasn't changed
    documents = document_store.filter_documents()
    assert len(documents) == len(sample_documents)

def test_vector_search(document_store, sample_documents):
    """Test vector search functionality."""
    # Write documents
    document_store.write_documents(sample_documents)
    
    # Create a query embedding
    query_embedding = [0.1] * VECTOR_DIMENSION
    
    # Perform vector search
    results = document_store.vector_search(query_embedding, top_k=3)
    
    # Verify results
    assert len(results) == 3
    assert all(hasattr(doc, "score") for doc in results)
    assert all(doc.score is not None for doc in results)
    
    # Verify results are sorted by score
    scores = [doc.score for doc in results]
    assert scores == sorted(scores, reverse=True)

def test_vector_search_with_filters(document_store, sample_documents):
    """Test vector search with filters."""
    # Write documents
    document_store.write_documents(sample_documents)
    
    # Create a query embedding
    query_embedding = [0.1] * VECTOR_DIMENSION
    
    # Define filters
    filters = {
        "field": "field2",
        "operator": ">",
        "value": 2
    }
    
    # Perform vector search with filters
    results = document_store.vector_search(
        query_embedding,
        top_k=3,
        filters=filters
    )
    
    # Verify results
    assert len(results) <= 3
    assert all(doc.meta["field2"] > 2 for doc in results)

def test_filter_documents_with_complex_filters(document_store, sample_documents):
    """Test filtering documents with complex filters."""
    # Write documents
    document_store.write_documents(sample_documents)
    
    # Define complex filters
    filters = {
        "operator": "and",
        "conditions": [
            {
                "field": "field2",
                "operator": ">=",
                "value": 1
            },
            {
                "field": "field2",
                "operator": "<=",
                "value": 3
            }
        ]
    }
    
    # Apply filters
    results = document_store.filter_documents(filters)
    
    # Verify results
    assert len(results) == 3
    assert all(1 <= doc.meta["field2"] <= 3 for doc in results)

def test_delete_documents(document_store, sample_documents):
    """Test document deletion."""
    # Write documents
    document_store.write_documents(sample_documents)
    
    # Get document IDs
    doc_ids = [doc.id for doc in sample_documents]
    
    # Delete some documents
    delete_ids = doc_ids[:2]
    document_store.delete_documents(delete_ids)
    
    # Verify remaining documents
    remaining_docs = document_store.filter_documents()
    assert len(remaining_docs) == len(sample_documents) - 2
    assert all(doc.id not in delete_ids for doc in remaining_docs)

def test_count_documents(document_store, sample_documents):
    """Test document counting."""
    # Write documents
    document_store.write_documents(sample_documents)
    
    # Count documents
    count = document_store.count_documents()
    assert count == len(sample_documents)
    
    # Delete some documents
    document_store.delete_documents([sample_documents[0].id])
    
    # Count again
    count = document_store.count_documents()
    assert count == len(sample_documents) - 1

def test_create_index_with_include_fields(document_store_params, mock_cluster, mock_query_result):
    """Test index creation with include fields"""
    document_store_params["index_params"] = IndexParams(
        dimension=768,
        similarity_metric=VectorSimilarityMetric.COSINE,
        include_fields=["field1", "field2"],
    )
    store = CouchbaseGSIDocumentStore(**document_store_params)
    mock_cluster.query.return_value = mock_query_result
    
    store.create_index()
    
    mock_cluster.query.assert_called_once()
    query_args = mock_cluster.query.call_args[0][0]
    assert "CREATE VECTOR INDEX test_index" in query_args
    assert "ON test_bucket.test_scope.test_collection (embedding VECTOR)" in query_args
    assert "INCLUDE (field1, field2)" in query_args
    assert "USING GSI" in query_args
    assert "'dimension': 768" in query_args
    assert "'similarity_metric': <VectorSimilarityMetric.COSINE: 'COSINE'>" in query_args
    assert "'include_fields' not in query_args"  # Verify include_fields is not in WITH clause

def test_composite_index_search(document_store_params, mock_cluster, mock_query_result):
    """Test vector search with composite index"""
    document_store_params["index_type"] = IndexType.COMPOSITE
    document_store_params["index_params"] = IndexParams(
        dimension=768,
        similarity_metric=VectorSimilarityMetric.COSINE,
        description="SQ8",
        include_fields=["field1", "field2"]
    )
    store = CouchbaseGSIDocumentStore(**document_store_params)
    query_embedding = [0.1] * 768
    
    mock_query_result.rows.return_value = [
        {
            "test_collection": {
                "id": "doc1",
                "content": "Test document 1",
                "embedding": [0.1] * 768,
                "field1": "value1",
                "field2": "value2"
            },
            "score": 0.95,
        }
    ]
    mock_cluster.query.return_value = mock_query_result
    
    results = store.vector_search(query_embedding, top_k=1)
    
    assert len(results) == 1
    assert results[0].id == "doc1"
    assert results[0].score == 0.95
    assert "field1" in results[0].meta
    assert "field2" in results[0].meta 