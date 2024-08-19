---
id: cluster_options
title: ClusterOptions
---

## Overview

The `CouchbaseClusterOptions` class configures various cluster-level options in Couchbase, including timeout settings, tracing configurations, and more.

## Classes

### `CouchbaseClusterOptions`

This class provides methods for initializing, serializing, and deserializing Couchbase cluster options.

#### Constructor

```python
@overload
    def __init__(
        self,
        profile=None, # type: Optional[KnownConfigProfiles]
        #timeout_options
        bootstrap_timeout=None,  # type: Optional[timedelta]
        resolve_timeout=None,  # type: Optional[timedelta]
        connect_timeout=None,  # type: Optional[timedelta]
        kv_timeout=None,  # type: Optional[timedelta]
        kv_durable_timeout=None,  # type: Optional[timedelta]
        views_timeout=None,  # type: Optional[timedelta]
        query_timeout=None,  # type: Optional[timedelta]
        analytics_timeout=None,  # type: Optional[timedelta]
        search_timeout=None,  # type: Optional[timedelta]
        management_timeout=None,  # type: Optional[timedelta]
        dns_srv_timeout=None,  # type: Optional[timedelta]
        idle_http_connection_timeout=None,  # type: Optional[timedelta]
        config_idle_redial_timeout=None,  # type: Optional[timedelta]
        config_total_timeout=None,  # type: Optional[timedelta]
        #timeout_options

        #tracing_options
        tracing_threshold_kv=None,  # type: Optional[timedelta]
        tracing_threshold_view=None,  # type: Optional[timedelta]
        tracing_threshold_query=None,  # type: Optional[timedelta]
        tracing_threshold_search=None,  # type: Optional[timedelta]
        tracing_threshold_analytics=None,  # type: Optional[timedelta]
        tracing_threshold_eventing=None,  # type: Optional[timedelta]
        tracing_threshold_management=None,  # type: Optional[timedelta]
        tracing_threshold_queue_size=None,  # type: Optional[int]
        tracing_threshold_queue_flush_interval=None,  # type: Optional[timedelta]
        tracing_orphaned_queue_size=None,  # type: Optional[int]
        tracing_orphaned_queue_flush_interval=None,  # type: Optional[timedelta]
        #tracing_options

        enable_tls=None,    # type: Optional[bool]
        enable_mutation_tokens=None,    # type: Optional[bool]
        enable_tcp_keep_alive=None,    # type: Optional[bool]
        ip_protocol=None,    # type: Optional[Union[IpProtocol, str]]
        enable_dns_srv=None,    # type: Optional[bool]
        show_queries=None,    # type: Optional[bool]
        enable_unordered_execution=None,    # type: Optional[bool]
        enable_clustermap_notification=None,    # type: Optional[bool]
        enable_compression=None,    # type: Optional[bool]
        enable_tracing=None,    # type: Optional[bool]
        enable_metrics=None,    # type: Optional[bool]
        network=None,    # type: Optional[str]
        tls_verify=None,    # type: Optional[Union[TLSVerifyMode, str]]
        tcp_keep_alive_interval=None,  # type: Optional[timedelta]
        config_poll_interval=None,  # type: Optional[timedelta]
        config_poll_floor=None,  # type: Optional[timedelta]
        max_http_connections=None,  # type: Optional[int]
        user_agent_extra=None,  # type: Optional[str]
        logging_meter_emit_interval=None,  # type: Optional[timedelta]
        log_redaction=None,  # type: Optional[bool]
        compression=None,  # type: Optional[Compression]
        compression_min_size=None,  # type: Optional[int]
        compression_min_ratio=None,  # type: Optional[float]
        dns_nameserver=None,  # type: Optional[str]
        dns_port=None,  # type: Optional[int]
        disable_mozilla_ca_certificates=None,  # type: Optional[bool]
        dump_configuration=None,  # type: Optional[bool]
    )
```

The constructor supports various options for cluster configuration, including timeouts, tracing, and network settings. These options are initialized via the constructor arguments.

#### Methods

- **`get_cluster_options(auth: Union[CouchbasePasswordAuthenticator, CouchbaseCertificateAuthenticator]) -> ClusterOptions`**: 

  Returns a `ClusterOptions` object configured with the provided authenticator and options.

  ```python
  def get_cluster_options(self, auth: Union[CouchbasePasswordAuthenticator | CouchbaseCertificateAuthenticator]) -> "ClusterOptions":
      ...
  ```

- **`to_dict() -> Dict[str, Any]`**: 

  Serializes the cluster options to a dictionary format. This method flattens timeout and tracing fields and converts enum fields to their corresponding values.

  ```python
  def to_dict(self) -> Dict[str, Any]:
      """
      Serializes the component to a dictionary.
  
      :returns:
          Dictionary with serialized data.
      """
      ...
  ```

- **`from_dict(data: Dict[str, Any]) -> "ClusterOptions"`**: 

  Deserializes the cluster options from a dictionary format. This method reconstructs timeout and tracing fields from seconds and maps enum fields back to their respective classes.

  ```python
  @classmethod
  def from_dict(cls, data: Dict[str, Any]) -> "ClusterOptions":
      """
      Deserializes the component from a dictionary.
  
      :param data:
          Dictionary to deserialize from.
      :returns:
            Deserialized component.
      """
      ...
  ```

## Usage

Here’s an example of how to use the `CouchbaseClusterOptions` class:

```python
from couchbase_haystack.document_stores import CouchbaseClusterOptions, CouchbasePasswordAuthenticator

auth = CouchbasePasswordAuthenticator(username="user", password="pass")
options = CouchbaseClusterOptions(enable_tls=True, network="default")
cluster_options = options.get_cluster_options(auth)
```