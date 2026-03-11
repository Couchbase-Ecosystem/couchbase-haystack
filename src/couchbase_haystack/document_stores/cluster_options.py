from datetime import timedelta
from typing import Any, ClassVar, Dict, List, Optional, Union, overload

from couchbase.options import ClusterOptions, Compression, IpProtocol, KnownConfigProfiles, TLSVerifyMode
from haystack import default_from_dict, default_to_dict

from .auth import CouchbaseCertificateAuthenticator, CouchbasePasswordAuthenticator


class CouchbaseClusterOptions(dict):
    """ClusterOptions is a dictionary that contains the options for the Couchbase cluster."""

    __cluster_level_timedelta_fields: ClassVar[List[str]] = [
        "tcp_keep_alive_interval",
        "config_poll_interval",
        "config_poll_floor",
        "logging_meter_emit_interval",
        # timeout fields as timeout and trace level delta fields are flattened in CouchbaseOptions class
        "bootstrap_timeout",
        "resolve_timeout",
        "connect_timeout",
        "kv_timeout",
        "kv_durable_timeout",
        "views_timeout",
        "query_timeout",
        "analytics_timeout",
        "search_timeout",
        "management_timeout",
        "dns_srv_timeout",
        "idle_http_connection_timeout",
        "config_idle_redial_timeout",
        "config_total_timeout",
        # timeout fields
        # tracing fields  as timeout and trace level delta fields are flattened in CouchbaseOptions class
        "tracing_threshold_kv",
        "tracing_threshold_view",
        "tracing_threshold_query",
        "tracing_threshold_search",
        "tracing_threshold_analytics",
        "tracing_threshold_eventing",
        "tracing_threshold_management",
        "tracing_threshold_queue_flush_interval",
        "tracing_orphaned_queue_flush_interval",
        # tracing fields
    ]
    __cluster_level_direct_fields: ClassVar[List[str]] = [
        "enable_tls",
        "enable_mutation_tokens",
        "enable_tcp_keep_alive",
        "enable_dns_srv",
        "show_queries",
        "enable_unordered_execution",
        "enable_clustermap_notification",
        "enable_compression",
        "enable_tracing",
        "enable_metrics",
        "network",
        "max_http_connections",
        "user_agent_extra",
        "log_redaction",
        "compression_min_size",
        "compression_min_ratio",
        "dns_nameserver",
        "dns_port",
        "disable_mozilla_ca_certificates",
        "dump_configuration",
        # tracing fields as timeout and trace level delta fields are flattened in CouchbaseOptions class
        "tracing_threshold_queue_size",
        "tracing_orphaned_queue_size",
        # tracing fields
    ]  # like int string , float etc

    __cluster_level_enum_fields: ClassVar[Dict[str, Any]] = {
        "ip_protocol": IpProtocol,
        "tls_verify": TLSVerifyMode,
        "compression": Compression,
        "profile": KnownConfigProfiles,
    }

    @overload
    def __init__(
        self,
        profile: Optional[KnownConfigProfiles] = None,
        # timeout_options
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
        # timeout_options
        # tracing_options
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
        # tracing_options
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
    ):
        """Initialize CouchbaseClusterOptions with explicit parameters.

        Args:
            profile: The profile to use for the Couchbase cluster. Defaults to None.
            bootstrap_timeout: The timeout for the bootstrap operation. Defaults to None.
            resolve_timeout: The timeout for the resolve operation. Defaults to None.
            connect_timeout: The timeout for the connect operation. Defaults to None.
            kv_timeout: The timeout for the KV operation. Defaults to None.
            kv_durable_timeout: The timeout for the KV durable operation. Defaults to None.
            views_timeout: The timeout for the views operation. Defaults to None.
            query_timeout: The timeout for the query operation. Defaults to None.
            analytics_timeout: The timeout for the analytics operation. Defaults to None.
            search_timeout: The timeout for the search operation. Defaults to None.
            management_timeout: The timeout for the management operation. Defaults to None.
            dns_srv_timeout: The timeout for the DNS SRV operation. Defaults to None.
            idle_http_connection_timeout: The timeout for idle HTTP connections. Defaults to None.
            config_idle_redial_timeout: The timeout for idle config redials. Defaults to None.
            config_total_timeout: The total timeout for config operations. Defaults to None.
            tracing_threshold_kv: The threshold for KV tracing. Defaults to None.
            tracing_threshold_view: The threshold for view tracing. Defaults to None.
            tracing_threshold_query: The threshold for query tracing. Defaults to None.
            tracing_threshold_search: The threshold for search tracing. Defaults to None.
            tracing_threshold_analytics: The threshold for analytics tracing. Defaults to None.
            tracing_threshold_eventing: The threshold for eventing tracing. Defaults to None.
            tracing_threshold_management: The threshold for management tracing. Defaults to None.
            tracing_threshold_queue_size: The queue size for tracing threshold. Defaults to None.
            tracing_threshold_queue_flush_interval: The interval for tracing threshold queue flushing. Defaults to None.
            tracing_orphaned_queue_size: The queue size for tracing orphaned events. Defaults to None.
            tracing_orphaned_queue_flush_interval: The interval for tracing orphaned queue flushing. Defaults to None.
            enable_tls: Whether to enable TLS. Defaults to None.
            enable_mutation_tokens: Whether to enable mutation tokens. Defaults to None.
            enable_tcp_keep_alive: Whether to enable TCP keep-alive. Defaults to None.
            ip_protocol: The IP protocol to use. Defaults to None.
            enable_dns_srv: Whether to enable DNS SRV. Defaults to None.
            show_queries: Whether to show queries. Defaults to None.
            enable_unordered_execution: Whether to enable unordered execution. Defaults to None.
            enable_clustermap_notification: Whether to enable clustermap notification. Defaults to None.
            enable_compression: Whether to enable compression. Defaults to None.
            enable_tracing: Whether to enable tracing. Defaults to None.
            enable_metrics: Whether to enable metrics. Defaults to None.
            network: The network to use. Defaults to None.
            tls_verify: The TLS verification mode. Defaults to None.
            tcp_keep_alive_interval: The interval for TCP keep-alive. Defaults to None.
            config_poll_interval: The interval for config polling. Defaults to None.
            config_poll_floor: The floor for config polling. Defaults to None.
            max_http_connections: The maximum number of HTTP connections. Defaults to None.
            user_agent_extra: Extra user agent information. Defaults to None.
            logging_meter_emit_interval: The interval for logging meter emission. Defaults to None.
            log_redaction: Whether to redact logs. Defaults to None.
            compression: The compression to use. Defaults to None.
            compression_min_size: The minimum size for compression. Defaults to None.
            compression_min_ratio: The minimum ratio for compression. Defaults to None.
            dns_nameserver: The DNS nameserver to use. Defaults to None.
            dns_port: The DNS port to use. Defaults to None.
            disable_mozilla_ca_certificates: Whether to disable Mozilla CA certificates. Defaults to None.
            dump_configuration: Whether to dump configuration. Defaults to None.
        """

    @overload
    def __init__(self, **kwargs):
        """Initialize CouchbaseClusterOptions with keyword arguments.

        Any parameter accepted by the explicit overload can be passed as a keyword argument.
        """

    def __init__(self, **kwargs):
        """Initialize CouchbaseClusterOptions by passing all keyword arguments to the parent dictionary class."""
        super().__init__(**kwargs)

    def get_cluster_options(
        self, auth: Union[CouchbasePasswordAuthenticator, CouchbaseCertificateAuthenticator]
    ) -> "ClusterOptions":
        """Creates a ClusterOptions object with the provided authenticator.

        Args:
            auth: The authenticator to use for the Couchbase cluster.

        Returns:
            A ClusterOptions object configured with the provided authenticator and any other options.
        """

        options = list(self.keys())
        obj = {}
        obj["authenticator"] = auth
        for option in options:
            obj[option] = self[option]
        return ClusterOptions(**obj)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the component to a dictionary.

        Returns:
            Dictionary with serialized data.
        """
        obj: Dict[str, Any] = {}

        # cluster level direct fields includes timeout and trace as they are flattened
        for f in CouchbaseClusterOptions.__cluster_level_timedelta_fields:
            delta_val: Optional[timedelta] = self.get(f)
            if delta_val is not None:
                obj[f] = delta_val.total_seconds()

        for f in CouchbaseClusterOptions.__cluster_level_direct_fields:
            df_val: Optional[Any] = self.get(f)
            if df_val is not None:
                obj[f] = df_val

        for f, enum_cls in CouchbaseClusterOptions.__cluster_level_enum_fields.items():
            val = self.get(f)
            if val is not None:
                obj[f] = val.value if isinstance(val, enum_cls) else val

        return default_to_dict(self, **obj)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CouchbaseClusterOptions":
        """Deserializes the component from a dictionary.

        Args:
            data: Dictionary to deserialize from.

        Returns:
            Deserialized component.
        """
        obj = {}
        # cluster level direct fields includes timeout and trace as they are flattened
        for f in CouchbaseClusterOptions.__cluster_level_timedelta_fields:
            if data["init_parameters"].get(f) is not None:
                obj[f] = timedelta(seconds=data["init_parameters"].get(f))

        for f in CouchbaseClusterOptions.__cluster_level_direct_fields:
            if data["init_parameters"].get(f) is not None:
                obj[f] = data["init_parameters"].get(f)

        for f, enum_cls in CouchbaseClusterOptions.__cluster_level_enum_fields.items():
            if data["init_parameters"].get(f) is not None:
                obj[f] = enum_cls(data["init_parameters"].get(f))

        data["init_parameters"] = obj
        return default_from_dict(cls, data)
