from datetime import timedelta
from typing import Any, ClassVar, Dict, List, Optional, Union, overload

from couchbase.options import ClusterOptions, Compression, IpProtocol, KnownConfigProfiles, TLSVerifyMode
from haystack import default_from_dict, default_to_dict

from .auth import CouchbaseCertificateAuthenticator, CouchbasePasswordAuthenticator


class CouchbaseClusterOptions(dict):
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
        """ClusterOptions instance."""

    @overload
    def __init__(self, **kwargs):
        """ClusterOptions instance."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_cluster_options(
        self, auth: Union[CouchbasePasswordAuthenticator | CouchbaseCertificateAuthenticator]
    ) -> "ClusterOptions":
        options = list(self.keys())
        obj = {}
        obj["authenticator"] = auth
        for option in options:
            obj[option] = self[option]
        return ClusterOptions(**obj)

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes the component to a dictionary.

        :returns:
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
    def from_dict(cls, data: Dict[str, Any]) -> "ClusterOptions":
        """
        Deserializes the component from a dictionary.

        :param data:
            Dictionary to deserialize from.
        :returns:
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
