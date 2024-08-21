import os

from unittest.mock import MagicMock, Mock, patch
import pytest
from couchbase_haystack import CouchbaseDocumentStore
from couchbase_haystack import CouchbaseEmbeddingRetriever, CouchbaseDocumentStore
from couchbase_haystack import CouchbasePasswordAuthenticator

from haystack.dataclasses import Document
from haystack import GeneratedAnswer, Pipeline
from haystack.components.builders.answer_builder import AnswerBuilder
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack.components.generators import HuggingFaceAPIGenerator
import couchbase.search as search
from couchbase.search import SearchQuery


@pytest.mark.unit
class TestRetrieverUnit:
    @pytest.fixture
    def doc_store(self):
        yield MagicMock(spec=CouchbaseDocumentStore)

    def test_to_dict(self, doc_store: MagicMock):
        ac_doc_store = CouchbaseDocumentStore(
            authenticator=CouchbasePasswordAuthenticator(),
            bucket="haystack_integration_test",
            scope="haystack_test_scope",
            collection="haystack_collection",
            vector_search_index="vector_search",
        )
        doc_store.to_dict.return_value = ac_doc_store.to_dict()
        retriever = CouchbaseEmbeddingRetriever(document_store=doc_store, top_k=15)
        serialized_retriever = retriever.to_dict()
        # assert serialized_store["init_parameters"].pop("collection_name").startswith("test_collection_")
        assert serialized_retriever == {
            "type": "couchbase_haystack.components.retrievers.embedding_retriever.CouchbaseEmbeddingRetriever",
            "init_parameters": {
                "top_k": 15,
                "document_store": {
                    "type": "couchbase_haystack.document_stores.document_store.CouchbaseDocumentStore",
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
                        "vector_search_index": "vector_search",
                    },
                },
            },
        }

    def test_from_dict(self):
        retriever = CouchbaseEmbeddingRetriever.from_dict(
            {
                "type": "couchbase_haystack.components.retrievers.embedding_retriever.CouchbaseEmbeddingRetriever",
                "init_parameters": {
                    "top_k": 15,
                    "document_store": {
                        "type": "couchbase_haystack.document_stores.document_store.CouchbaseDocumentStore",
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
                            "bucket": "haystack_integration_test",
                            "scope": "haystack_test_scope",
                            "collection": "haystack_collection",
                            "vector_search_index": "vector_search",
                        },
                    },
                },
            }
        )
        assert retriever.top_k == 15
        assert isinstance(retriever.document_store.authenticator, CouchbasePasswordAuthenticator)
        assert retriever.document_store.bucket == "haystack_integration_test"
        assert retriever.document_store.scope_name == "haystack_test_scope"
        assert retriever.document_store.collection_name == "haystack_collection"
        assert retriever.document_store.vector_search_index == "vector_search"

    def test_run(self, doc_store: MagicMock):
        doc_store._embedding_retrieval.return_value = [Document(content="Who created the Dothraki vocabulary?")]
        retriever = CouchbaseEmbeddingRetriever(document_store=doc_store, top_k=15)
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
            "retriever": {"top_k": 3, "search_query": sq},
        }
        result = rag_pipeline.run(data, include_outputs_from={"query_embedder"})
        doc_store._embedding_retrieval.assert_called_once_with(
            query_embedding=result["query_embedder"]["embedding"],
            top_k=3,
            search_query=data["retriever"]["search_query"],
            limit=None,
        )
        assert result["retriever"]["documents"] == doc_store._embedding_retrieval.return_value
