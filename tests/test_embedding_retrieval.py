# SPDX-FileCopyrightText: 2023-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0
import os
from typing import List

import pytest

from haystack.dataclasses.document import  Document
from haystack.utils import Secret
from couchbase_haystack.document_stores import CouchbaseDocumentStore, CouchbasePasswordAuthenticator
from pandas import DataFrame
from couchbase.cluster import Cluster, ClusterOptions
from couchbase.options import ClusterOptions
from couchbase.auth import PasswordAuthenticator
from couchbase.management.logic.search_index_logic import SearchIndex
from couchbase.exceptions import SearchIndexNotFoundException



from datetime import timedelta
from sentence_transformers import SentenceTransformer

from .common import common

import json

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
class TestEmbeddingRetrieval:
    @pytest.fixture()
    def document_store(self):
        bucket_name = "haystack_integration_test"
        scope_name = "haystack_test_scope"
        collection_name = "haystack_collection"
        cluster = Cluster(
                os.environ["CONNECTION_STRING"], ClusterOptions(
                    authenticator=PasswordAuthenticator(username=os.environ["USER_NAME"], password=os.environ["PASSWORD"]),
                    enable_tcp_keep_alive = True
                ),
            )
        cluster.wait_until_ready(timeout=timedelta(seconds=30))
        bucket= cluster.bucket(bucket_name=bucket_name)
        collection_manager = bucket.collections()
        common.create_scope_if_not_exists(collection_manager,scope_name)
        common.create_collection_if_not_exists(collection_manager,scope_name, collection_name)
        scope = bucket.scope(scope_name)
        collection = scope.collection(collection_name)
        index_definition = common.load_json_file("./tests/vector_index.json")
        index_definition["params"]["mapping"]["types"]["haystack_test_scope.haystack_collection"]["properties"]["embedding"]["fields"][0]["dims"]=3
        sim = scope.search_indexes()
        try:
            sim.get_index(index_name= index_definition["name"])
        except SearchIndexNotFoundException as e:
            #print("all clear ",e)
            search_index = SearchIndex(name=index_definition["name"],
                                source_name=index_definition["sourceName"],
                                source_type=index_definition["sourceType"],
                                params=index_definition["params"],
                                plan_params=index_definition["planParams"])
            sim.upsert_index(search_index)

        store = CouchbaseDocumentStore(
            cluster_connection_string=os.environ["CONNECTION_STRING"],
            cluster_options=ClusterOptions(authenticator=CouchbasePasswordAuthenticator(
                username=Secret.from_env_var("USER_NAME"), password=Secret.from_env_var("PASSWORD"))),
            bucket=bucket_name,
            scope=scope_name,
            collection=collection_name,
            vector_search_index=index_definition["name"],
        )

        store.write_documents([
            Document(content="red color", embedding=[1.0,0.0,0.0], meta={"color": "red", "number": 1}),
            Document(content="blue color", embedding=[0.0,1.0,0.0], meta={"color": "blue", "number": 2}),
            Document(content="grey color", embedding=[0.0,0.0,1.0], meta={"color": "grey", "number": 3}),
            Document(content="light grey color", embedding=[0.0,0.1,0.9], meta={"color": "light grey", "number": 4}),
            ])
        
        yield store
        result = scope.search_indexes().drop_index(index_definition["name"])
        #print("dropped index successfully",result)
        result = cluster.query
        (f"drop collection {bucket_name}.{scope_name}.{collection_name}").execute()
        #print("dropped collection successfully",result)
        cluster.close()

    def test_embedding_retrieval(self, document_store: CouchbaseDocumentStore): 
        query_embedding = [0.9,0.1,0.0]
        results = document_store._embedding_retrieval(query_embedding=query_embedding, top_k=3, filters={})
        assert len(results) == 3
        assert results[0].content == "red color"
        assert results[1].content == "blue color"
        assert results[0].score > results[1].score

    def test_embedding_retrieval_with_filter(self, document_store: CouchbaseDocumentStore): 
        query_embedding = [0.9,0.0,0.0]
        results = document_store._embedding_retrieval(query_embedding=query_embedding, top_k=1, search={"field" : "meta.number", "operator": "==", "value": 3})
        assert len(results) == 2
        assert results[0].content == "red color"
        assert results[1].content == "grey color"
        assert results[0].score > results[1].score

        