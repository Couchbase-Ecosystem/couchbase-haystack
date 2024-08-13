# SPDX-FileCopyrightText: 2023-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0
from unittest.mock import MagicMock, Mock, patch

import pytest

from typing import Dict, Any

from haystack.dataclasses.document import Document
from haystack.utils import Secret
from couchbase_haystack import CouchbaseDocumentStore
from couchbase_haystack import CouchbasePasswordAuthenticator
from couchbase.result import SearchResult

from couchbase.management.logic.collections_logic import ScopeSpec, CollectionSpec

class Client:
    def __init__(self, cluster : MagicMock, scope: MagicMock, collection: MagicMock):
        self.cluster = cluster
        self.scope = scope
        self.collection = collection

class Row:
    def __init__(self, id :str, score :int = 1 ):
        self.id = id
        self.score = score   

class GetResult:
    def __init__(self, success:bool, value : Dict[str, Any] ):
        self.success= success
        self.id = id
        self.value = value

class MultiResult:
    def __init__(self, all_ok: bool, results: Dict[str,GetResult],exceptions :Dict[str, Any] = None):
        self.all_ok = all_ok
        self.results= results
        self.exceptions = exceptions


class TestRetriever:

    @pytest.fixture
    def mock_client(self):
        with patch(
            "haystack_integrations.document_stores.couchbase.document_store.Cluster"
        ) as mock_cb_cluster:
            
            cluster = mock_cb_cluster.return_value
            bucket = cluster.bucket.return_value
            scope = bucket.scope.return_value
            collection = scope.collection.return_value
            bucket.collections.return_value.get_all_scopes.return_value = [
                ScopeSpec(
                    "haystack_scope_name",
                    [
                        CollectionSpec(collection_name="haystack_collection_name")
                    ]
                )
            ]
            client = Client(cluster=cluster, scope=scope, collection=collection)
            yield client

    def test_init_default(self, mock_client : Client):
        store = CouchbaseDocumentStore(
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
        scope = mock_client.scope

        scope.search.return_value = SearchResult(search_request=[Row(id="1a")])
        mock_client.collection.get_multi.return_value = MultiResult(all_ok=True, results={"1a": GetResult(success=True, value={"content":"text"})})
        doc = store.filter_documents({})
        
        mock_client.cluster.bucket.return_value.scope.assert_called_once_with("haystack_scope_name")
        assert doc == [Document(id = "1a",content="text", score=1)]
       