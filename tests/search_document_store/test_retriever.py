import os

from unittest.mock import MagicMock, Mock, patch
import pytest
from couchbase_haystack import (
    CouchbaseSearchDocumentStore,
    CouchbaseSearchEmbeddingRetriever,
    CouchbasePasswordAuthenticator,
)

from haystack.dataclasses import Document
from haystack import GeneratedAnswer, Pipeline
from haystack.components.builders.answer_builder import AnswerBuilder
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack.components.generators import HuggingFaceAPIGenerator
import couchbase.search as search
from couchbase.search import SearchQuery
from tests.common.common import IS_GLOBAL_LEVEL_INDEX


@pytest.mark.unit
class TestRetrieverUnit:
    @pytest.fixture
    def doc_store(self):
        yield MagicMock(spec=CouchbaseSearchDocumentStore)

    def test_to_dict(self, doc_store: MagicMock):
        ac_doc_store = CouchbaseSearchDocumentStore(
            authenticator=CouchbasePasswordAuthenticator(),
            bucket="test_bucket",
            scope="test_scope",
            collection="test_collection",
            vector_search_index="vector_search",
            is_global_level_index=IS_GLOBAL_LEVEL_INDEX,
        )
        doc_store.to_dict.return_value = ac_doc_store.to_dict()
        retriever = CouchbaseSearchEmbeddingRetriever(document_store=doc_store, top_k=15)
        serialized_retriever = retriever.to_dict()
        # assert serialized_store["init_parameters"].pop("collection_name").startswith("test_collection_")
        assert serialized_retriever == {
            "type": "couchbase_haystack.components.retrievers.embedding_retriever.CouchbaseSearchEmbeddingRetriever",
            "init_parameters": {
                "top_k": 15,
                "document_store": {
                    "type": "couchbase_haystack.document_stores.document_store.CouchbaseSearchDocumentStore",
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
                        "bucket": "test_bucket",
                        "scope": "test_scope",
                        "collection": "test_collection",
                        "vector_search_index": "vector_search",
                        'is_global_level_index': IS_GLOBAL_LEVEL_INDEX,
                    },
                },
            },
        }

    def test_from_dict(self):
        retriever = CouchbaseSearchEmbeddingRetriever.from_dict(
            {
                "type": "couchbase_haystack.components.retrievers.embedding_retriever.CouchbaseSearchEmbeddingRetriever",
                "init_parameters": {
                    "top_k": 15,
                    "document_store": {
                        "type": "couchbase_haystack.document_stores.document_store.CouchbaseSearchDocumentStore",
                        "init_parameters": {
                            "cluster_connection_string": {
                                "type": "env_var",
                                "env_vars": ["CB_CONNECTION_STRING"],
                                "strict": True,
                            },
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
                            "bucket": "test_bucket",
                            "scope": "test_scope",
                            "collection": "test_collection",
                            "vector_search_index": "vector_search",
                        },
                    },
                },
            }
        )
        assert retriever.top_k == 15
        assert isinstance(retriever.document_store.authenticator, CouchbasePasswordAuthenticator)
        assert retriever.document_store.bucket_name == "test_bucket"
        assert retriever.document_store.scope_name == "test_scope"
        assert retriever.document_store.collection_name == "test_collection"
        assert retriever.document_store.vector_search_index == "vector_search"

    def test_run(self, doc_store: MagicMock):
        doc_store._embedding_retrieval.return_value = [Document(content="Who created the Dothraki vocabulary?")]
        retriever = CouchbaseSearchEmbeddingRetriever(document_store=doc_store, top_k=15)
        rag_pipeline = Pipeline()
        rag_pipeline.add_component(
            "query_embedder",
            SentenceTransformersTextEmbedder(model="sentence-transformers/all-MiniLM-L6-v2", progress_bar=False),
        )
        rag_pipeline.add_component("retriever", retriever)
        rag_pipeline.connect("query_embedder", "retriever.query_embedding")

        # Ask a question on the data you just added.
        question = "Who created the Dothraki vocabulary?"
        sq = search.BooleanQuery(
            must=search.ConjunctionQuery(search.MatchQuery("term2", field="field1"), search.MatchQuery("term", field="field3"))
        )
        data = {
            "query_embedder": {"text": question},
            "retriever": {"top_k": 3, "search_query": sq, "filters": {"field": "meta.color", "operator": "==", "value": "red"}},
        }
        result = rag_pipeline.run(data, include_outputs_from={"query_embedder"})
        doc_store._embedding_retrieval.assert_called_once_with(
            query_embedding=result["query_embedder"]["embedding"],
            top_k=3,
            search_query=data["retriever"]["search_query"],  # type: ignore
            filters=data["retriever"]["filters"],  # type: ignore
            limit=None,
        )
        assert result["retriever"]["documents"] == doc_store._embedding_retrieval.return_value

    def test_run_with_limit(self, doc_store: MagicMock):
        # Setup mock return value
        mock_docs = [Document(content="Who created the Dothraki vocabulary?")]
        doc_store._embedding_retrieval.return_value = mock_docs
        retriever = CouchbaseSearchEmbeddingRetriever(document_store=doc_store, top_k=15)
        # Example embedding and filters
        test_embedding = [0.1, 0.2, 0.3]
        sq = search.BooleanQuery(
            must=search.ConjunctionQuery(search.MatchQuery("term2", field="field1"), search.MatchQuery("term", field="field3"))
        )
        test_filters = {"field": "meta.color", "operator": "==", "value": "red"}
        test_limit = 2
        # Call run directly with explicit limit
        result = retriever.run(
            query_embedding=test_embedding,
            top_k=3,
            search_query=sq,
            filters=test_filters,
            limit=test_limit,
        )
        # Assert that explicit limit is passed through
        doc_store._embedding_retrieval.assert_called_once_with(
            query_embedding=test_embedding,
            top_k=3,
            search_query=sq,
            filters=test_filters,
            limit=test_limit,
        )
        assert result["documents"] == mock_docs
