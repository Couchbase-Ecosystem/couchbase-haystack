from .auth import CouchbasePasswordAuthenticator, CouchbaseCertificateAuthenticator 
from haystack import default_from_dict, default_to_dict
from typing import Any, Dict, Optional, Union, overload
from couchbase.options import IpProtocol, TLSVerifyMode, Compression, ClusterOptions, KnownConfigProfiles
from datetime import timedelta

class CouchbaseClusterOptions(dict):
    __cluster_level_timedelta_fields = [
        "tcp_keep_alive_interval", "config_poll_interval", "config_poll_floor", "logging_meter_emit_interval",
        #timeout fields as timeout and trace level delta fields are flattened in CouchbaseOptions class
        "bootstrap_timeout","resolve_timeout","connect_timeout","kv_timeout","kv_durable_timeout",
        "views_timeout","query_timeout","analytics_timeout","search_timeout","management_timeout",
        "dns_srv_timeout","idle_http_connection_timeout","config_idle_redial_timeout", "config_total_timeout",
        #timeout fields

        #tracing fields  as timeout and trace level delta fields are flattened in CouchbaseOptions class
        "tracing_threshold_kv","tracing_threshold_view","tracing_threshold_query","tracing_threshold_search",
        "tracing_threshold_analytics","tracing_threshold_eventing","tracing_threshold_management",
        "tracing_threshold_queue_flush_interval","tracing_orphaned_queue_flush_interval",
        #tracing fields

    ]
    __cluster_level_direct_fields = [
        "enable_tls","enable_mutation_tokens","enable_tcp_keep_alive","enable_dns_srv",
        "show_queries","enable_unordered_execution","enable_clustermap_notification","enable_compression",
        "enable_tracing","enable_metrics","network", "max_http_connections", "user_agent_extra", "log_redaction",
        "compression_min_size","compression_min_ratio","dns_nameserver",
        "dns_port","disable_mozilla_ca_certificates","dump_configuration",

        #tracing fields as timeout and trace level delta fields are flattened in CouchbaseOptions class
        "tracing_threshold_queue_size","tracing_orphaned_queue_size"
        #tracing fields
    ] # like int string , float etc

    __cluster_level_enum_fields = {"ip_protocol": IpProtocol ,"tls_verify" : TLSVerifyMode, "compression": Compression, "profile": KnownConfigProfiles}
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
    ):
        """ClusterOptions instance."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_cluster_options(self, auth: Union[CouchbasePasswordAuthenticator | CouchbaseCertificateAuthenticator]) -> "ClusterOptions":
        options = list(self.keys())
        obj = {
        }
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

        obj = {
        }

        # cluster level direct fields includes timeout and trace as they are flattened
        for f in CouchbaseClusterOptions.__cluster_level_timedelta_fields:
            if self.get(f):
                obj[f] =  self.get(f).total_seconds()

        for f in CouchbaseClusterOptions.__cluster_level_direct_fields:
            if self.get(f):
                obj[f] =  self.get(f)

        for f, enum_cls in CouchbaseClusterOptions.__cluster_level_enum_fields.items():
            val = self.get(f)
            if val:
                obj[f] =  val.value if isinstance(val, enum_cls) else val
                print("enum",f, isinstance(val, enum_cls),obj[f])

                  
        return default_to_dict(self,**obj)
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
            if data["init_parameters"].get(f) != None:
                obj[f] = timedelta(seconds=data["init_parameters"].get(f))  

        for f in CouchbaseClusterOptions.__cluster_level_direct_fields:
            if data["init_parameters"].get(f) != None:
                obj[f] = data["init_parameters"].get(f) 

        for f, enum_cls in CouchbaseClusterOptions.__cluster_level_enum_fields.items():
            if data["init_parameters"].get(f) != None:
                obj[f] = enum_cls(data["init_parameters"].get(f))               

        #print(obj)
        data["init_parameters"] = obj
        return default_from_dict(cls, data)
