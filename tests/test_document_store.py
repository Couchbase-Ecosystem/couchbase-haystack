# SPDX-FileCopyrightText: 2023-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0
import os

from unittest.mock import MagicMock, Mock, patch
from uuid import uuid1
import time
import pytest
from typing import List, Dict, Any, Optional
from haystack.dataclasses.document import ByteStream, Document
from haystack.testing.document_store import DocumentStoreBaseTests
from haystack.utils import Secret
from couchbase_haystack import CouchbaseDocumentStore
from pandas import DataFrame
from couchbase.cluster import Cluster, ClusterOptions
from couchbase.options import ClusterOptions, KnownConfigProfiles
from couchbase.auth import PasswordAuthenticator
from couchbase_haystack import CouchbaseClusterOptions
from couchbase_haystack import CouchbasePasswordAuthenticator
from couchbase.management.logic.search_index_logic import SearchIndex
from couchbase.exceptions import SearchIndexNotFoundException
from datetime import timedelta
from sentence_transformers import SentenceTransformer
from couchbase.management.logic.collections_logic import ScopeSpec, CollectionSpec
from couchbase.result import SearchResult

from .common import common


model = SentenceTransformer('all-MiniLM-L6-v2')


@patch("couchbase_haystack.document_stores.document_store.Cluster")
def test_init_is_lazy(_mock_cluster):
    store = CouchbaseDocumentStore(
        cluster_connection_string="couchbases://localhost",
        cluster_options=CouchbaseClusterOptions(),
        authenticator=CouchbasePasswordAuthenticator(),
        bucket="haystack_test_bucket",
        scope="scope_name",
        collection="collection_name",
        vector_search_index="vector_index",
    )
    _mock_cluster.assert_not_called()


@pytest.mark.skipif(
    "CONNECTION_STRING" not in os.environ,
    reason="Couchbase cluster connection string not provided",
)
@pytest.mark.skipif(
    "USER_NAME" not in os.environ,
    reason="Couchbase cluster username not provided",
)
@pytest.mark.skipif(
    "PASSWORD" not in os.environ,
    reason="Couchbase cluster password not provided",
)
@pytest.mark.integration
class TestDocumentStore(DocumentStoreBaseTests):
    @pytest.fixture()
    def document_store(self):
        bucket_name = "haystack_integration_test"
        scope_name = "haystack_test_scope"
        collection_name = "haystack_collection"
        cluster_opts = ClusterOptions(
            authenticator=PasswordAuthenticator(username=os.environ["USER_NAME"], password=os.environ["PASSWORD"]),
            enable_tcp_keep_alive=True,
        )
        cluster_opts.apply_profile(KnownConfigProfiles.WanDevelopment)

        cluster = Cluster(os.environ["CONNECTION_STRING"], cluster_opts)

        cluster.wait_until_ready(timeout=timedelta(seconds=30))
        bucket = cluster.bucket(bucket_name=bucket_name)
        collection_manager = bucket.collections()
        common.create_scope_if_not_exists(collection_manager, scope_name)
        common.create_collection_if_not_exists(collection_manager, scope_name, collection_name)
        scope = bucket.scope(scope_name)
        collection = scope.collection(collection_name)
        index_definition = common.load_json_file("./tests/vector_index.json")

        sim = scope.search_indexes()
        try:
            sim.get_index(index_name=index_definition["name"])
        except SearchIndexNotFoundException as e:
            search_index = SearchIndex(
                name=index_definition["name"],
                source_name=index_definition["sourceName"],
                source_type=index_definition["sourceType"],
                params=index_definition["params"],
                plan_params=index_definition["planParams"],
            )
            sim.upsert_index(search_index)

        store = CouchbaseDocumentStore(
            cluster_connection_string=Secret.from_env_var("CONNECTION_STRING"),
            cluster_options=CouchbaseClusterOptions(profile=KnownConfigProfiles.WanDevelopment),
            authenticator=CouchbasePasswordAuthenticator(
                username=Secret.from_env_var("USER_NAME"), password=Secret.from_env_var("PASSWORD")
            ),
            bucket=bucket_name,
            scope=scope_name,
            collection=collection_name,
            vector_search_index=index_definition["name"],
        )
        yield store
        result = scope.search_indexes().drop_index(index_definition["name"])
        # print("dropped index successfully",result)
        result = cluster.query(f"drop collection {bucket_name}.{scope_name}.{collection_name}").execute()
        # print("dropped collection successfully",result)
        cluster.close()

    def assert_documents_are_equal(self, received: List[Document], expected: List[Document]):

        for r in received:
            r.score = None
            r.embedding = None
        received_dict = {doc.id: doc for doc in received}
        received = []
        for doc in expected:
            received.append(received_dict.get(doc.id))
            doc.embedding = None
        # print([doc.to_dict(flatten=False) if doc else doc for doc in received])
        # print([doc.to_dict(flatten=False) for doc in expected])
        super().assert_documents_are_equal(received, expected)

    def test_no_filters(self, document_store: CouchbaseDocumentStore):
        """Test filter_documents() with empty filters"""
        self.assert_documents_are_equal(document_store.filter_documents(), [])
        self.assert_documents_are_equal(document_store.filter_documents(filters={}), [])
        docs = [Document(content="test doc")]
        document_store.write_documents(docs)
        self.assert_documents_are_equal(document_store.filter_documents(), docs)
        self.assert_documents_are_equal(document_store.filter_documents(filters={}), docs)

    def test_write_documents(self, document_store: CouchbaseDocumentStore):
        documents = [
            Document(id=uuid1().hex, content="Haystack is an amazing tool for search."),
            Document(id=uuid1().hex, content="We are using pre-trained models to generate embeddings."),
            Document(id=uuid1().hex, content="The weather is sunny today."),
        ]
        for doc in documents:
            embedding = model.encode(doc.content).tolist()
            doc.embedding = embedding

        assert document_store.write_documents(documents) == 3
        retrieved_docs = document_store.filter_documents()
        assert len(retrieved_docs) == 3
        retrieved_docs.sort(key=lambda x: x.id)
        self.assert_documents_are_equal(retrieved_docs, documents)

    def test_write_blob(self, document_store: CouchbaseDocumentStore):
        bytestream = ByteStream(b"test", meta={"meta_key": "meta_value"}, mime_type="mime_type")
        documents = [Document(blob=bytestream)]
        for doc in documents:
            # Assuming blob_content is in bytes, decode it to string if necessary
            embedding = model.encode(bytestream.data.decode('utf-8')).tolist()
            doc.embedding = embedding
        assert document_store.write_documents(documents) == 1
        retrieved_docs = document_store.filter_documents()
        time.sleep(30)
        self.assert_documents_are_equal(retrieved_docs, documents)

    def test_write_dataframe(self, document_store: CouchbaseDocumentStore):
        dataframe = DataFrame({"col1": [1, 2], "col2": [3, 4]})
        docs = [Document(dataframe=dataframe)]
        document_store.write_documents(docs)
        retrieved_docs = document_store.filter_documents()
        self.assert_documents_are_equal(retrieved_docs, docs)

    def test_comparison_in1(self, document_store, filterable_docs):
        """Test filter_documents() with 'in' comparator"""
        document_store.write_documents(filterable_docs)
        # time.sleep(2000)
        result = document_store.filter_documents({"field": "meta.number", "operator": "in", "value": [10, -10]})
        assert len(result)
        expected = [d for d in filterable_docs if d.meta.get("number") is not None and d.meta["number"] in [10, -10]]
        self.assert_documents_are_equal(result, expected)

    def test_complex_filter(self, document_store, filterable_docs):
        document_store.write_documents(filterable_docs)
        filters = {
            "operator": "OR",
            "conditions": [
                {
                    "operator": "AND",
                    "conditions": [
                        {"field": "meta.number", "operator": "==", "value": 100},
                        {"field": "meta.chapter", "operator": "==", "value": "intro"},
                    ],
                },
                {
                    "operator": "AND",
                    "conditions": [
                        {"field": "meta.page", "operator": "==", "value": "90"},
                        {"field": "meta.chapter", "operator": "==", "value": "conclusion"},
                    ],
                },
            ],
        }

        result = document_store.filter_documents(filters=filters)

        self.assert_documents_are_equal(
            result,
            [
                d
                for d in filterable_docs
                if (d.meta.get("number") == 100 and d.meta.get("chapter") == "intro")
                or (d.meta.get("page") == "90" and d.meta.get("chapter") == "conclusion")
            ],
        )


class DocumentStore:
    def __init__(self, document_store: CouchbaseDocumentStore, cluster: MagicMock, scope: MagicMock, collection: MagicMock):
        self.document_store = document_store
        self.cluster = cluster
        self.scope = scope
        self.collection = collection


class Row:
    def __init__(self, id: str, score: int = 1):
        self.id = id
        self.score = score


class GetResult:
    def __init__(self, success: bool, value: Dict[str, Any]):
        self.success = success
        self.id = id
        self.value = value


class MultiResult:
    def __init__(self, all_ok: bool, results: Dict[str, GetResult], exceptions: Optional[Dict[str, Any]] = None):
        self.all_ok = all_ok
        self.results = results
        self.exceptions = exceptions


@pytest.mark.unit
class TestDocumentStoreUnit:
    @pytest.fixture
    def document_store(self):
        with patch("couchbase_haystack.document_stores.document_store.Cluster") as mock_cb_cluster:

            cluster = mock_cb_cluster.return_value
            bucket = cluster.bucket.return_value
            scope = bucket.scope.return_value
            collection = scope.collection.return_value
            bucket.collections.return_value.get_all_scopes.return_value = [
                ScopeSpec("haystack_test_scope", [CollectionSpec(collection_name="haystack_collection")])
            ]
            store = CouchbaseDocumentStore(
                cluster_connection_string=Secret.from_env_var("CONNECTION_STRING"),
                authenticator=CouchbasePasswordAuthenticator(
                    username=Secret.from_env_var("USER_NAME"), password=Secret.from_env_var("PASSWORD")
                ),
                cluster_options=CouchbaseClusterOptions(profile=KnownConfigProfiles.WanDevelopment),
                bucket="haystack_integration_test",
                scope="haystack_test_scope",
                collection="haystack_collection",
                vector_search_index="vector_search",
            )
            client = DocumentStore(document_store=store, cluster=cluster, scope=scope, collection=collection)
            yield client

    def test_to_dict(self, document_store: DocumentStore):
        serialized_store = document_store.document_store.to_dict()
        # assert serialized_store["init_parameters"].pop("collection_name").startswith("test_collection_")
        assert serialized_store == {
            'type': 'couchbase_haystack.document_stores.document_store.CouchbaseDocumentStore',
            'init_parameters': {
                'cluster_connection_string': {'type': 'env_var', 'env_vars': ['CONNECTION_STRING'], 'strict': True},
                'authenticator': {
                    'type': 'couchbase_haystack.document_stores.auth.CouchbasePasswordAuthenticator',
                    'init_parameters': {
                        'username': {'type': 'env_var', 'env_vars': ['USER_NAME'], 'strict': True},
                        'password': {'type': 'env_var', 'env_vars': ['PASSWORD'], 'strict': True},
                        'cert_path': None,
                    },
                },
                'cluster_options': {
                    'type': 'couchbase_haystack.document_stores.cluster_options.CouchbaseClusterOptions',
                    'init_parameters': {'profile': 'wan_development'},
                },
                'bucket': 'haystack_integration_test',
                'scope': 'haystack_test_scope',
                'collection': 'haystack_collection',
                'vector_search_index': 'vector_search',
            },
        }

    def test_from_dict(self):
        docstore = CouchbaseDocumentStore.from_dict(
            {
                'type': 'couchbase_haystack.document_stores.document_store.CouchbaseDocumentStore',
                'init_parameters': {
                    'cluster_connection_string': {'type': 'env_var', 'env_vars': ['CONNECTION_STRING'], 'strict': True},
                    'authenticator': {
                        'type': 'couchbase_haystack.document_stores.auth.CouchbasePasswordAuthenticator',
                        'init_parameters': {
                            'username': {'type': 'env_var', 'env_vars': ['USER_NAME'], 'strict': True},
                            'password': {'type': 'env_var', 'env_vars': ['PASSWORD'], 'strict': True},
                            'cert_path': None,
                        },
                    },
                    'cluster_options': {
                        'type': 'couchbase_haystack.document_stores.cluster_options.CouchbaseClusterOptions',
                        'init_parameters': {'profile': 'wan_development'},
                    },
                    'bucket': 'haystack_integration_test',
                    'scope': 'haystack_test_scope',
                    'collection': 'haystack_collection',
                    'vector_search_index': 'vector_search',
                },
            }
        )
        assert docstore.cluster_connection_string == Secret.from_env_var("CONNECTION_STRING")
        assert docstore.bucket == "haystack_integration_test"
        assert docstore.scope_name == "haystack_test_scope"
        assert docstore.collection_name == "haystack_collection"
        assert docstore.vector_search_index == "vector_search"
        assert docstore.cluster_options["profile"] == KnownConfigProfiles.WanDevelopment

    def test_init_default(self, document_store: DocumentStore, monkeypatch):
        monkeypatch.setenv("CONNECTION_STRING", "value_one")
        monkeypatch.setenv("USER_NAME", "value_one")
        monkeypatch.setenv("PASSWORD", "value_one")
        scope = document_store.scope

        scope.search.return_value = SearchResult(search_request=[Row(id="1a")])
        document_store.collection.get_multi.return_value = MultiResult(
            all_ok=True, results={"1a": GetResult(success=True, value={"content": "text"})}
        )
        doc = document_store.document_store.filter_documents({})

        document_store.cluster.bucket.return_value.scope.assert_called_once_with("haystack_test_scope")
        assert doc == [Document(id="1a", content="text", score=1)]
