import os

from unittest.mock import MagicMock, Mock, patch
import pytest
from couchbase.n1ql import QueryScanConsistency
from couchbase_haystack import (
    CouchbaseQueryDocumentStore,
    CouchbaseQueryEmbeddingRetriever,
    CouchbasePasswordAuthenticator,
    CouchbaseClusterOptions,
    CouchbaseQueryOptions,
    QueryVectorSearchType
)

from haystack.dataclasses import Document


@pytest.mark.unit
class TestQueryRetrieverUnit:
    @pytest.fixture
    def query_doc_store(self):
        yield MagicMock(spec=CouchbaseQueryDocumentStore)

    def test_to_dict(self, query_doc_store: MagicMock):
        # Create an actual instance to get its default dict representation
        ac_doc_store = CouchbaseQueryDocumentStore(
            authenticator=CouchbasePasswordAuthenticator(),
            bucket="haystack_integration_test",
            scope="haystack_test_scope",
            collection="haystack_collection",
            index_name="vector_gsi_index",
            search_type=QueryVectorSearchType.ANN,
            similarity="cosine",
            query_options=CouchbaseQueryOptions(scan_consistency=QueryScanConsistency.NOT_BOUNDED)
        )
        # Mock the to_dict method of the fixture to return the actual dict
        query_doc_store.to_dict.return_value = ac_doc_store.to_dict()

        retriever = CouchbaseQueryEmbeddingRetriever(document_store=query_doc_store, top_k=5)
        serialized_retriever = retriever.to_dict()

        assert serialized_retriever == {
            "type": "couchbase_haystack.components.retrievers.embedding_retriever.CouchbaseQueryEmbeddingRetriever",
            "init_parameters": {
                "top_k": 5,
                "document_store": {
                    "type": "couchbase_haystack.document_stores.document_store.CouchbaseQueryDocumentStore",
                    "init_parameters": {
                        "cluster_connection_string": {"type": "env_var", "env_vars": ["CB_CONNECTION_STRING"], "strict": True},
                        "authenticator": {
                            "type": "couchbase_haystack.document_stores.auth.CouchbasePasswordAuthenticator",
                            "init_parameters": {
                                "username": {"type": "env_var", "env_vars": ["CB_USERNAME"], "strict": True},
                                "password": {"type": "env_var", "env_vars": ["CB_PASSWORD"], "strict": True},
                                "cert_path": None,
                            },
                        },
                        "cluster_options": {
                            "type": "couchbase_haystack.document_stores.cluster_options.CouchbaseClusterOptions",
                            "init_parameters": {},
                        },
                        "bucket": "haystack_integration_test",
                        "scope": "haystack_test_scope",
                        "collection": "haystack_collection",
                        "index_name": "vector_gsi_index",
                        "query_vector_search_params": {
                            "type": "couchbase_haystack.document_stores.document_store.QueryVectorSearchType",
                             "init_parameters": {
                                "search_type": "ANN",
                                "similarity": "cosine"
                            }
                        },
                         "query_options": {
                             "type": "couchbase_haystack.document_stores.document_store.CouchbaseQueryOptions",
                             "init_parameters": {
                                "timeout": 60.0,
                                "scan_consistency": "not_bounded"
                             }
                         }
                    },
                },
            },
        }

    def test_from_dict(self):
        retriever = CouchbaseQueryEmbeddingRetriever.from_dict(
            {
                "type": "couchbase_haystack.components.retrievers.embedding_retriever.CouchbaseQueryEmbeddingRetriever",
                "init_parameters": {
                    "top_k": 5,
                    "document_store": {
                        "type": "couchbase_haystack.document_stores.document_store.CouchbaseQueryDocumentStore",
                        "init_parameters": {
                            "cluster_connection_string": {"type": "env_var", "env_vars": ["CB_CONNECTION_STRING"], "strict": True},
                            "authenticator": {
                                "type": "couchbase_haystack.document_stores.auth.CouchbasePasswordAuthenticator",
                                "init_parameters": {
                                    "username": {"type": "env_var", "env_vars": ["CB_USERNAME"], "strict": True},
                                    "password": {"type": "env_var", "env_vars": ["CB_PASSWORD"], "strict": True},
                                },
                            },
                            "cluster_options": {
                                "type": "couchbase_haystack.document_stores.cluster_options.CouchbaseClusterOptions",
                                "init_parameters": {},
                            },
                             "bucket": "haystack_test_bucket",
                             "scope": "scope_name",
                             "collection": "collection_name",
                             "index_name": "vector_gsi_index",
                             "query_vector_search_params": {
                                 "type": "couchbase_haystack.document_stores.document_store.QueryVectorSearchType",
                                 "init_parameters": {
                                    "search_type": "KNN",
                                    "similarity": "dot_product"
                                 }
                             },
                             "query_options": {
                                "type": "couchbase_haystack.document_stores.document_store.CouchbaseQueryOptions",
                                "init_parameters": {
                                    "scan_consistency": "request_plus",
                                    "timeout": 30.0
                                }
                            }
                        },
                    },
                },
            }
        )
        assert retriever.top_k == 5
        assert isinstance(retriever.document_store, CouchbaseQueryDocumentStore)
        assert retriever.document_store.bucket_name == "haystack_test_bucket"
        assert retriever.document_store.scope_name == "scope_name"
        assert retriever.document_store.collection_name == "collection_name"
        assert retriever.document_store.index_name == "vector_gsi_index"
        assert retriever.document_store.search_type == QueryVectorSearchType.KNN
        assert retriever.document_store.similarity == "dot_product"
        assert isinstance(retriever.document_store.query_options, CouchbaseQueryOptions)
        assert retriever.document_store.query_options.scan_consistency == QueryScanConsistency.REQUEST_PLUS
        assert retriever.document_store.query_options.timeout.total_seconds() == 30.0


    def test_run(self, query_doc_store: MagicMock):
        mock_docs = [Document(content="Test doc 1"), Document(content="Test doc 2")]
        query_doc_store._embedding_retrieval.return_value = mock_docs

        retriever = CouchbaseQueryEmbeddingRetriever(document_store=query_doc_store, top_k=5)
        
        test_embedding = [0.1] * 768 # Example embedding
        test_filters = {"field": "meta.genre", "operator": "==", "value": "fiction"}
        
        result = retriever.run(query_embedding=test_embedding, top_k=3, filters=test_filters)

        # Assert _embedding_retrieval was called correctly
        query_doc_store._embedding_retrieval.assert_called_once_with(
            query_embedding=test_embedding,
            top_k=3,
            filters=test_filters,
            limit=3, # limit defaults to top_k in run method
        )
        # Assert the result contains the documents returned by the mock
        assert result["documents"] == mock_docs
    def test_run_with_limit(self, query_doc_store: MagicMock):
        mock_docs = [Document(content="Test doc limit")]
        query_doc_store._embedding_retrieval.return_value = mock_docs

        retriever = CouchbaseQueryEmbeddingRetriever(document_store=query_doc_store, top_k=10) # Default top_k

        test_embedding = [0.5] * 768
        test_filters = {"field": "meta.year", "operator": ">", "value": 2000}
        test_limit = 2 # Explicit limit different from top_k

        result = retriever.run(query_embedding=test_embedding, top_k=5, filters=test_filters, limit=test_limit)

        # Assert _embedding_retrieval was called with the explicit limit
        query_doc_store._embedding_retrieval.assert_called_once_with(
            query_embedding=test_embedding,
            top_k=5, # top_k from run call
            filters=test_filters,
            limit=test_limit, # Explicit limit passed
        )
        assert result["documents"] == mock_docs

