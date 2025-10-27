# SPDX-FileCopyrightText: 2023-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0
import pytest
from datetime import timedelta
from unittest.mock import Mock, patch
from haystack.dataclasses import Document
from haystack.document_stores.errors import DocumentStoreError
from couchbase.exceptions import DocumentExistsException
from couchbase_haystack.document_stores.document_store import (
    CouchbaseQueryDocumentStore,
    QueryVectorSearchType,
    QueryScanConsistency,
    CouchbaseQueryOptions,
)
from couchbase_haystack.document_stores.auth import CouchbasePasswordAuthenticator
from couchbase_haystack.document_stores.cluster_options import CouchbaseClusterOptions
from haystack.document_stores.types import DuplicatePolicy
from haystack.utils.auth import Secret
import os

# Set test environment variables
os.environ["CB_CONNECTION_STRING"] = "couchbase://localhost"
os.environ["CB_USERNAME"] = "test_user"
os.environ["CB_PASSWORD"] = "test_password"


# Test fixtures
@pytest.fixture
def mock_collection():
    """Create a mock collection."""
    collection = Mock()
    collection.insert_multi = Mock()
    collection.get_multi = Mock()
    collection.remove_multi = Mock()
    collection.upsert_multi = Mock()
    return collection


@pytest.fixture
def mock_scope_spec():
    """Create a mock scope specification."""
    scope_spec = Mock()
    scope_spec.name = "test_scope"
    collection_spec = Mock()
    collection_spec.name = "test_collection"
    scope_spec.collections = [collection_spec]
    return scope_spec


@pytest.fixture
def mock_bucket(mock_scope_spec):
    """Create a mock bucket."""
    bucket = Mock()
    bucket.collections = Mock()
    bucket.collections.return_value.get_all_scopes = Mock(return_value=[mock_scope_spec])
    bucket.scope = Mock()
    return bucket


@pytest.fixture
def mock_scope():
    """Create a mock scope."""
    scope = Mock()
    scope.collection = Mock()
    return scope


@pytest.fixture
def mock_query_result():
    """Create a mock query result."""
    result = Mock()
    result.rows = Mock()
    result.rows.return_value = []
    return result


@pytest.fixture
def mock_cluster(mock_collection, mock_bucket, mock_scope, mock_query_result):
    """Create a mock cluster."""
    cluster = Mock()
    cluster.query = Mock(return_value=mock_query_result)
    cluster.bucket = Mock(return_value=mock_bucket)
    cluster.bucket.return_value.scope = Mock(return_value=mock_scope)
    cluster.bucket.return_value.scope.return_value.collection = Mock(return_value=mock_collection)
    cluster.wait_until_ready = Mock()
    return cluster


@pytest.fixture
def authenticator():
    """Create a test authenticator with hardcoded credentials."""
    return CouchbasePasswordAuthenticator(
        username=Secret.from_env_var("CB_USERNAME"), password=Secret.from_env_var("CB_PASSWORD")
    )


@pytest.fixture
def cluster_options():
    """Create test cluster options."""
    return CouchbaseClusterOptions()


@pytest.fixture
def document_store_params(authenticator, cluster_options):
    """Create test document store parameters."""
    return {
        "authenticator": authenticator,
        "cluster_options": cluster_options,
        "bucket": "test_bucket",
        "scope": "test_scope",
        "collection": "test_collection",
        "search_type": QueryVectorSearchType.ANN,
        "similarity": "cosine",
        "query_options": CouchbaseQueryOptions(scan_consistency=QueryScanConsistency.REQUEST_PLUS, timeout=timedelta(seconds=10)),
    }


@pytest.fixture
def sample_documents():
    return [
        Document(
            id="doc1",
            content="Test document 1",
            meta={"field1": "value1"},
            embedding=[0.1] * 768,
        ),
        Document(
            id="doc2",
            content="Test document 2",
            meta={"field1": "value2"},
            embedding=[0.2] * 768,
        ),
    ]


@pytest.fixture(autouse=True)
def mock_couchbase(mock_cluster):
    """Mock Couchbase Cluster class for all tests."""
    with patch("couchbase_haystack.document_stores.document_store.Cluster", return_value=mock_cluster):
        yield mock_cluster


# Test cases
def test_init(document_store_params):
    """Test initialization of CouchbaseGSIDocumentStore"""
    store = CouchbaseQueryDocumentStore(**document_store_params)
    assert store.bucket_name == "test_bucket"
    assert store.scope_name == "test_scope"
    assert store.collection_name == "test_collection"
    assert store.search_type == QueryVectorSearchType.ANN
    assert store.similarity == "COSINE"


def test_init_invalid_collection_name(document_store_params):
    """Test initialization with invalid collection name"""
    document_store_params["collection"] = "invalid@collection"
    with pytest.raises(ValueError, match="Invalid collection name"):
        CouchbaseQueryDocumentStore(**document_store_params)


def test_connection_property(document_store_params, mock_cluster):
    """Test connection property initialization"""
    store = CouchbaseQueryDocumentStore(**document_store_params)
    connection = store.connection
    assert connection == mock_cluster
    mock_cluster.wait_until_ready.assert_called_once_with(timeout=timedelta(seconds=60))


def test_scope_property(document_store_params, mock_cluster, mock_bucket, mock_scope_spec):
    """Test scope property initialization"""
    store = CouchbaseQueryDocumentStore(**document_store_params)
    mock_cluster.bucket.return_value = mock_bucket
    mock_bucket.collections.return_value.get_all_scopes.return_value = [mock_scope_spec]
    mock_bucket.scope.return_value = mock_scope_spec

    scope = store.scope
    assert scope == mock_bucket.scope.return_value
    mock_bucket.scope.assert_called_once_with("test_scope")


def test_scope_property_not_found(document_store_params, mock_cluster, mock_bucket):
    """Test scope property when scope does not exist"""
    store = CouchbaseQueryDocumentStore(**document_store_params)
    mock_cluster.bucket.return_value = mock_bucket
    mock_bucket.collections.return_value.get_all_scopes.return_value = [Mock(name="other_scope", collections=[])]

    with pytest.raises(ValueError, match="Scope 'test_scope' does not exist"):
        _ = store.scope


def test_collection_property(document_store_params, mock_cluster, mock_bucket, mock_scope):
    """Test collection property initialization"""
    store = CouchbaseQueryDocumentStore(**document_store_params)
    mock_cluster.bucket.return_value = mock_bucket
    mock_bucket.scope.return_value = mock_scope

    collection = store.collection
    assert collection == mock_scope.collection.return_value
    mock_scope.collection.assert_called_once_with("test_collection")


# def test_create_index(document_store_params, mock_cluster, mock_query_result):
#     """Test index creation"""
#     store = CouchbaseQueryDocumentStore(**document_store_params)
#     mock_cluster.query.return_value = mock_query_result

#     store.create_index()

#     mock_cluster.query.assert_called_once()
#     query_args = mock_cluster.query.call_args[0][0]
#     assert "CREATE VECTOR INDEX test_index" in query_args
#     assert "ON test_bucket.test_scope.test_collection (embedding VECTOR)" in query_args
#     assert "USING GSI" in query_args
#     assert "'dimension': 768" in query_args
#     assert "'similarity': 'cosine'" in query_args

# def test_drop_index(document_store_params, mock_cluster, mock_query_result):
#     """Test index dropping"""
#     store = CouchbaseQueryDocumentStore(**document_store_params)
#     mock_cluster.query.return_value = mock_query_result

#     store.drop_index()

#     expected_query = "DROP INDEX test_bucket.test_scope.test_collection.test_index"
#     mock_cluster.query.assert_called_once_with(expected_query)


def test_count_documents(document_store_params, mock_scope, mock_query_result):
    """Test document counting"""
    store = CouchbaseQueryDocumentStore(**document_store_params)
    mock_query_result.execute.return_value = [{"count": 5}]
    mock_scope.query.return_value = mock_query_result

    count = store.count_documents()
    assert count == 5


def test_write_documents(document_store_params, mock_collection, sample_documents):
    """Test document writing"""
    store = CouchbaseQueryDocumentStore(**document_store_params)
    store._collection = mock_collection

    mock_result = Mock()
    mock_result.all_ok = True
    mock_collection.insert_multi.return_value = mock_result

    written_count = store.write_documents(sample_documents)

    assert written_count == 2
    mock_collection.insert_multi.assert_called_once()
    call_args = mock_collection.insert_multi.call_args[0][0]
    assert len(call_args) == 2
    assert "doc1" in call_args
    assert "doc2" in call_args


def test_write_documents_duplicate_error(document_store_params, mock_collection, sample_documents):
    """Test document writing with duplicate documents"""
    store = CouchbaseQueryDocumentStore(**document_store_params)
    store._collection = mock_collection

    mock_result = Mock()
    mock_result.all_ok = False
    mock_result.exceptions = {"doc1": DocumentExistsException("Document exists")}
    mock_collection.insert_multi.return_value = mock_result

    with pytest.raises(DocumentStoreError):
        store.write_documents(sample_documents)


def test_delete_documents(document_store_params, mock_collection):
    """Test document deletion"""
    store = CouchbaseQueryDocumentStore(**document_store_params)
    store._collection = mock_collection

    document_ids = ["doc1", "doc2"]
    store.delete_documents(document_ids)

    mock_collection.remove_multi.assert_called_once_with(keys=document_ids)


def test_vector_search(document_store_params, mock_cluster, mock_query_result):
    """Test vector search"""
    store = CouchbaseQueryDocumentStore(**document_store_params)
    query_embedding = [0.1] * 768

    mock_query_result.rows.return_value = [
        {
            "id": "doc1",
            "content": "Test document 1",
            "embedding": [0.1] * 768,
            "score": 0.95,
        }
    ]
    mock_cluster.query.return_value = mock_query_result

    results = store._embedding_retrieval(query_embedding, top_k=1)

    assert len(results) == 1
    assert results[0].id == "doc1"
    assert results[0].content == "Test document 1"
    assert results[0].score == 0.95


def test_vector_search_empty_embedding(document_store_params):
    """Test vector search with empty embedding"""
    store = CouchbaseQueryDocumentStore(**document_store_params)
    query_embedding = []

    with pytest.raises(ValueError, match="Query embedding must not be empty"):
        store._embedding_retrieval(query_embedding)


def test_filter_documents(document_store_params, mock_scope, mock_query_result, comparison_filters):
    """Test document filtering"""
    store = CouchbaseQueryDocumentStore(**document_store_params)

    mock_query_result.rows.return_value = [
        {
            "id": "doc1",
            "content": "Test document 1",
            "field1": "value1",
        }
    ]
    mock_scope.query.return_value = mock_query_result

    results = store.filter_documents(comparison_filters["equality"])

    assert len(results) == 1
    assert results[0].id == "doc1"
    assert results[0].content == "Test document 1"
    assert results[0].meta["field1"] == "value1"


def test_connection_property_timeout(document_store_params):
    """Test connection timeout handling"""
    store = CouchbaseQueryDocumentStore(**document_store_params)

    with patch("couchbase_haystack.document_stores.document_store.Cluster") as mock:
        mock.return_value = Mock()
        mock.return_value.wait_until_ready = Mock(side_effect=TimeoutError("Connection timeout"))
        with pytest.raises(DocumentStoreError, match="Failed to establish connection: Connection timeout"):
            _ = store.connection


def test_collection_property_not_found(document_store_params, mock_cluster, mock_bucket):
    """Test collection property when collection does not exist"""
    store = CouchbaseQueryDocumentStore(**document_store_params)
    mock_cluster.bucket.return_value = mock_bucket

    # Mock a scope with a different collection name
    scope_spec = Mock()
    scope_spec.name = "test_scope"
    collection_spec = Mock()
    collection_spec.name = "other_collection"
    scope_spec.collections = [collection_spec]
    mock_bucket.collections.return_value.get_all_scopes.return_value = [scope_spec]

    with pytest.raises(ValueError, match="Collection 'test_collection' does not exist"):
        _ = store.collection


def test_write_documents_empty_list(document_store_params, mock_collection):
    """Test writing empty list of documents"""
    store = CouchbaseQueryDocumentStore(**document_store_params)
    store._collection = mock_collection  # Directly set the collection to avoid scope/bucket lookup
    documents = []

    written_count = store.write_documents(documents)
    assert written_count == 0
    mock_collection.insert_multi.assert_not_called()
    mock_collection.upsert_multi.assert_not_called()


def test_write_documents_invalid_type(document_store_params, mock_collection):
    """Test writing documents with invalid type"""
    store = CouchbaseQueryDocumentStore(**document_store_params)
    store._collection = mock_collection

    with pytest.raises(ValueError, match="param 'documents' must contain a list of objects of type Document"):
        store.write_documents([{"id": "doc1"}])


def test_write_documents_upsert_policy(document_store_params, mock_collection, sample_documents):
    """Test document writing with upsert policy"""
    store = CouchbaseQueryDocumentStore(**document_store_params)
    store._collection = mock_collection

    mock_result = Mock()
    mock_result.all_ok = True
    mock_collection.upsert_multi.return_value = mock_result

    written_count = store.write_documents(sample_documents, policy=DuplicatePolicy.OVERWRITE)

    assert written_count == 2
    mock_collection.upsert_multi.assert_called_once()
    mock_collection.insert_multi.assert_not_called()


def test_delete_documents_empty_list(document_store_params, mock_collection):
    """Test deleting empty list of documents"""
    store = CouchbaseQueryDocumentStore(**document_store_params)
    store._collection = mock_collection

    store.delete_documents([])
    mock_collection.remove_multi.assert_not_called()


def test_vector_search_with_filters(document_store_params, mock_cluster, mock_query_result, comparison_filters):
    """Test vector search with filters"""
    store = CouchbaseQueryDocumentStore(**document_store_params)
    query_embedding = [0.1] * 768

    mock_query_result.rows.return_value = [
        {
            "id": "doc1",
            "content": "Test document 1",
            "embedding": [0.1] * 768,
            "score": 0.95,
        }
    ]
    mock_cluster.query.return_value = mock_query_result

    results = store._embedding_retrieval(query_embedding, top_k=1, filters=comparison_filters["equality"])

    assert len(results) == 1
    assert results[0].id == "doc1"
    assert results[0].score == 0.95


def test_vector_search_composite_index(document_store_params, mock_cluster, mock_query_result):
    """Test vector search with composite index"""
    store = CouchbaseQueryDocumentStore(**document_store_params)
    query_embedding = [0.1] * 768

    mock_query_result.rows.return_value = [
        {
            "id": "doc1",
            "content": "Test document 1",
            "embedding": [0.1] * 768,
            "score": 0.95,
        }
    ]
    mock_cluster.query.return_value = mock_query_result

    results = store._embedding_retrieval(query_embedding, top_k=1)

    assert len(results) == 1
    assert results[0].id == "doc1"
    assert results[0].score == 0.95


def test_vector_search_query_error(document_store_params, mock_cluster):
    """Test vector search with query error"""
    store = CouchbaseQueryDocumentStore(**document_store_params)
    query_embedding = [0.1] * 768

    mock_cluster.query.side_effect = Exception("Query failed")

    with pytest.raises(DocumentStoreError, match="Failed to retrieve documents with vector search"):
        store._embedding_retrieval(query_embedding)


def test_filter_documents_complex_filters(document_store_params, mock_scope, mock_query_result, nested_filters):
    """Test document filtering with complex nested filters"""
    store = CouchbaseQueryDocumentStore(**document_store_params)

    mock_query_result.rows.return_value = [
        {
            "id": "doc1",
            "content": "Test document 1",
            "age": 25,
            "role": "admin",
        }
    ]
    mock_scope.query.return_value = mock_query_result

    results = store.filter_documents(nested_filters["and_with_or"])

    assert len(results) == 1
    assert results[0].id == "doc1"
    assert results[0].meta["age"] == 25
    assert results[0].meta["role"] == "admin"


def test_filter_documents_invalid_filters(document_store_params, mock_cluster, invalid_filters):
    """Test document filtering with invalid filters"""
    store = CouchbaseQueryDocumentStore(**document_store_params)

    for filter_name, invalid_filter in invalid_filters.items():
        with pytest.raises(Exception):
            store.filter_documents(invalid_filter)


def test_filter_documents_date_filters(document_store_params, mock_scope, mock_query_result, date_filters):
    """Test document filtering with date filters"""
    store = CouchbaseQueryDocumentStore(**document_store_params)

    mock_query_result.rows.return_value = [
        {
            "id": "doc1",
            "content": "Test document 1",
            "created_at": "2023-01-01T12:00:00",
        }
    ]
    mock_scope.query.return_value = mock_query_result

    results = store.filter_documents(date_filters["equality"])

    assert len(results) == 1
    assert results[0].id == "doc1"
    assert results[0].meta["created_at"] == "2023-01-01T12:00:00"


def test_filter_documents_field_path_filters(document_store_params, mock_scope, mock_query_result, field_path_filters):
    """Test document filtering with field path filters"""
    store = CouchbaseQueryDocumentStore(**document_store_params)

    mock_query_result.rows.return_value = [
        {"id": "doc1", "content": "Test document 1", "metadata": {"year": 2023, "author": {"name": "John Doe"}}}
    ]
    mock_scope.query.return_value = mock_query_result

    results = store.filter_documents(field_path_filters["nested_logical"])

    assert len(results) == 1
    assert results[0].id == "doc1"
    assert results[0].meta["metadata"]["year"] == 2023
    assert results[0].meta["metadata"]["author"]["name"] == "John Doe"


def test_serialization_deserialization(document_store_params):
    """Test serialization and deserialization of document store"""
    store = CouchbaseQueryDocumentStore(**document_store_params)

    # Serialize
    serialized = store.to_dict()

    # Verify serialized data contains all required fields
    init_params = serialized["init_parameters"]
    assert "authenticator" in init_params
    assert "cluster_options" in init_params
    assert "bucket" in init_params
    assert "scope" in init_params
    assert "collection" in init_params
    assert "search_type" in init_params
    assert "similarity" in init_params
    assert "query_options" in init_params

    # Deserialize
    deserialized = CouchbaseQueryDocumentStore.from_dict(serialized)

    # Verify deserialized object has correct attributes
    assert deserialized.bucket == store.bucket
    assert deserialized.scope_name == store.scope_name
    assert deserialized.collection_name == store.collection_name
    assert deserialized.search_type == store.search_type
    assert deserialized.similarity == store.similarity
    assert deserialized.query_options.scan_consistency == store.query_options.scan_consistency
    assert deserialized.query_options.timeout.total_seconds() == store.query_options.timeout.total_seconds()
