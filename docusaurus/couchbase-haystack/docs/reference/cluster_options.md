---
id: cluster_options
title: ClusterOptions
---

# Couchbase Cluster Options

This module provides the `CouchbaseClusterOptions` class, which allows for the configuration and management of cluster-level options in a Couchbase environment. This class is designed to be flexible, supporting a wide range of configuration parameters and enabling serialization and deserialization for easy storage and retrieval of configurations.

## Class Overview

### `CouchbaseClusterOptions`

The `CouchbaseClusterOptions` class inherits from `dict` and encapsulates various cluster-level configuration options for a Couchbase cluster. It supports a wide range of settings including timeouts, tracing, and network configurations.

#### Initialization

```python
@overload
def __init__(
    self,
    profile: Optional[KnownConfigProfiles] = None,
    # Various timeout options
    bootstrap_timeout: Optional[timedelta] = None,
    resolve_timeout: Optional[timedelta] = None,
    connect_timeout: Optional[timedelta] = None,
    kv_timeout: Optional[timedelta] = None,
    kv_durable_timeout: Optional[timedelta] = None,
    views_timeout: Optional[timedelta] = None,
    query_timeout: Optional[timedelta] = None,
    analytics_timeout: Optional[timedelta] = None,
    search_timeout: Optional[timedelta] = None,
    management_timeout: Optional[timedelta] = None,
    dns_srv_timeout: Optional[timedelta] = None,
    idle_http_connection_timeout: Optional[timedelta] = None,
    config_idle_redial_timeout: Optional[timedelta] = None,
    config_total_timeout: Optional[timedelta] = None,
    # Tracing options
    tracing_threshold_kv: Optional[timedelta] = None,
    tracing_threshold_view: Optional[timedelta] = None,
    tracing_threshold_query: Optional[timedelta] = None,
    tracing_threshold_search: Optional[timedelta] = None,
    tracing_threshold_analytics: Optional[timedelta] = None,
    tracing_threshold_eventing: Optional[timedelta] = None,
    tracing_threshold_management: Optional[timedelta] = None,
    tracing_threshold_queue_size: Optional[int] = None,
    tracing_threshold_queue_flush_interval: Optional[timedelta] = None,
    tracing_orphaned_queue_size: Optional[int] = None,
    tracing_orphaned_queue_flush_interval: Optional[timedelta] = None,
    # Other options
    enable_tls: Optional[bool] = None,
    enable_mutation_tokens: Optional[bool] = None,
    enable_tcp_keep_alive: Optional[bool] = None,
    ip_protocol: Optional[Union[IpProtocol, str]] = None,
    enable_dns_srv: Optional[bool] = None,
    show_queries: Optional[bool] = None,
    enable_unordered_execution: Optional[bool] = None,
    enable_clustermap_notification: Optional[bool] = None,
    enable_compression: Optional[bool] = None,
    enable_tracing: Optional[bool] = None,
    enable_metrics: Optional[bool] = None,
    network: Optional[str] = None,
    tls_verify: Optional[Union[TLSVerifyMode, str]] = None,
    tcp_keep_alive_interval: Optional[timedelta] = None,
    config_poll_interval: Optional[timedelta] = None,
    config_poll_floor: Optional[timedelta] = None,
    max_http_connections: Optional[int] = None,
    user_agent_extra: Optional[str] = None,
    logging_meter_emit_interval: Optional[timedelta] = None,
    log_redaction: Optional[bool] = None,
    compression: Optional[Compression] = None,
    compression_min_size: Optional[int] = None,
    compression_min_ratio: Optional[float] = None,
    dns_nameserver: Optional[str] = None,
    dns_port: Optional[int] = None,
    disable_mozilla_ca_certificates: Optional[bool] = None,
    dump_configuration: Optional[bool] = None,
)
```

- This initializer accepts a wide range of optional parameters, covering various aspects of Couchbase cluster configuration including timeouts, tracing, TLS, network settings, and more.


**Example Usage:**

```python
options = CouchbaseClusterOptions(
    enable_tls=True,
    kv_timeout=timedelta(seconds=2.5),
    max_http_connections=10,
)
```

#### `get_cluster_options`

```python
def get_cluster_options(
    self, auth: Union[CouchbasePasswordAuthenticator, CouchbaseCertificateAuthenticator]
) -> "ClusterOptions"
```

**Input Parameters:**
- `auth` (Union[CouchbasePasswordAuthenticator, CouchbaseCertificateAuthenticator]): The authentication mechanism to be used with the cluster.

**Response:**
- Returns a `ClusterOptions` instance, initialized with the authentication method and the provided configuration options.

**Example Usage:**

```python
auth = CouchbasePasswordAuthenticator(username="user", password="pass")
cluster_options = options.get_cluster_options(auth=auth)
```

#### `to_dict`

```python
def to_dict() -> Dict[str, Any]
```

**Response:**
- Returns a dictionary containing the serialized state of the `CouchbaseClusterOptions` instance. The method ensures that all supported fields are converted appropriately, including converting `timedelta` objects to seconds.

**Example Usage:**

```python
options_dict = options.to_dict()
```

#### `from_dict`

```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> "CouchbaseClusterOptions"
```

**Input Parameters:**
- `data` (Dict[str, Any]): A dictionary containing the serialized state of a `CouchbaseClusterOptions`.

**Response:**
- Returns a `CouchbaseClusterOptions` instance reconstructed from the provided dictionary.

**Example Usage:**

```python
options_instance = CouchbaseClusterOptions.from_dict(options_dict)
```