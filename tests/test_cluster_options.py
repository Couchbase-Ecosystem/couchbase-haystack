from couchbase_haystack import CouchbaseClusterOptions
from couchbase.options import Compression, IpProtocol, TLSVerifyMode
from couchbase.auth import PasswordAuthenticator
from datetime import timedelta


class TestCouchbaseClusterOptions:
    def test(self):
        def assert_output(opt):
            # tracing_options
            assert opt["bootstrap_timeout"] == bootstrap_timeout
            assert opt["resolve_timeout"] == resolve_timeout
            assert opt["connect_timeout"] == connect_timeout
            assert opt["kv_timeout"] == kv_timeout
            assert opt["kv_durable_timeout"] == kv_durable_timeout
            assert opt["views_timeout"] == views_timeout
            assert opt["query_timeout"] == query_timeout
            assert opt["analytics_timeout"] == analytics_timeout
            assert opt["search_timeout"] == search_timeout
            assert opt["management_timeout"] == management_timeout
            assert opt["dns_srv_timeout"] == dns_srv_timeout
            assert opt["idle_http_connection_timeout"] == idle_http_connection_timeout
            assert opt["config_idle_redial_timeout"] == config_idle_redial_timeout
            assert opt["config_total_timeout"] == config_total_timeout
            # timeout_options
            # tracing_options
            assert opt["tracing_threshold_kv"] == tracing_threshold_kv
            assert opt["tracing_threshold_view"] == tracing_threshold_view
            assert opt["tracing_threshold_query"] == tracing_threshold_query
            assert opt["tracing_threshold_search"] == tracing_threshold_search
            assert opt["tracing_threshold_analytics"] == tracing_threshold_analytics
            assert opt["tracing_threshold_eventing"] == tracing_threshold_eventing
            assert opt["tracing_threshold_management"] == tracing_threshold_management
            assert opt["tracing_threshold_queue_size"] == tracing_threshold_queue_size
            assert opt["tracing_threshold_queue_flush_interval"] == tracing_threshold_queue_flush_interval
            assert opt["tracing_orphaned_queue_size"] == tracing_orphaned_queue_size
            assert opt["tracing_orphaned_queue_flush_interval"] == tracing_orphaned_queue_flush_interval
            # tracing_options

            assert opt["enable_tls"] == enable_tls
            assert opt["enable_mutation_tokens"] == enable_mutation_tokens
            assert opt["enable_tcp_keep_alive"] == enable_tcp_keep_alive
            assert opt["ip_protocol"] == ip_protocol
            assert opt["enable_dns_srv"] == enable_dns_srv
            assert opt["show_queries"] == show_queries
            assert opt["enable_unordered_execution"] == enable_unordered_execution
            assert opt["enable_clustermap_notification"] == enable_clustermap_notification
            assert opt["enable_compression"] == enable_compression
            assert opt["enable_tracing"] == enable_tracing
            assert opt["enable_metrics"] == enable_metrics
            assert opt["network"] == network
            assert opt["tls_verify"] == tls_verify
            assert opt["tcp_keep_alive_interval"] == tcp_keep_alive_interval
            assert opt["config_poll_interval"] == config_poll_interval
            assert opt["config_poll_floor"] == config_poll_floor
            assert opt["max_http_connections"] == max_http_connections
            assert opt["user_agent_extra"] == user_agent_extra
            assert opt["logging_meter_emit_interval"] == logging_meter_emit_interval
            assert opt["log_redaction"] == log_redaction
            assert opt["compression"] == compression
            assert opt["compression_min_size"] == compression_min_size
            assert opt["compression_min_ratio"] == compression_min_ratio
            assert opt["dns_nameserver"] == dns_nameserver
            assert opt["dns_port"] == dns_port
            assert opt["disable_mozilla_ca_certificates"] == disable_mozilla_ca_certificates
            assert opt["dump_configuration"] == dump_configuration

        # timeout_options
        bootstrap_timeout = timedelta(seconds=10)
        resolve_timeout = timedelta(seconds=11)
        connect_timeout = timedelta(seconds=12)
        kv_timeout = timedelta(seconds=13)
        kv_durable_timeout = timedelta(seconds=14)
        views_timeout = timedelta(seconds=15)
        query_timeout = timedelta(seconds=16)
        analytics_timeout = timedelta(seconds=17)
        search_timeout = timedelta(seconds=18)
        management_timeout = timedelta(seconds=19)
        dns_srv_timeout = timedelta(seconds=20)
        idle_http_connection_timeout = timedelta(seconds=21)
        config_idle_redial_timeout = timedelta(seconds=22)
        config_total_timeout = timedelta(seconds=23)
        # timeout_options
        # tracing_options
        tracing_threshold_kv = timedelta(seconds=24)
        tracing_threshold_view = timedelta(seconds=25)
        tracing_threshold_query = timedelta(seconds=26)
        tracing_threshold_search = timedelta(seconds=27)
        tracing_threshold_analytics = timedelta(seconds=28)
        tracing_threshold_eventing = timedelta(seconds=29)
        tracing_threshold_management = timedelta(seconds=30)
        tracing_threshold_queue_size = 1
        tracing_threshold_queue_flush_interval = timedelta(seconds=31)
        tracing_orphaned_queue_size = 2
        tracing_orphaned_queue_flush_interval = timedelta(seconds=32)
        # tracing_options

        enable_tls = True
        enable_mutation_tokens = True
        enable_tcp_keep_alive = True
        ip_protocol = IpProtocol.ForceIPv4
        enable_dns_srv = True
        show_queries = True
        enable_unordered_execution = True
        enable_clustermap_notification = True
        enable_compression = True
        enable_tracing = True
        enable_metrics = True
        network = "test_network"
        tls_verify = TLSVerifyMode.PEER
        tcp_keep_alive_interval = timedelta(33)
        config_poll_interval = timedelta(34)
        config_poll_floor = timedelta(35)
        max_http_connections = 10
        user_agent_extra = "haystack_integration"
        logging_meter_emit_interval = timedelta(36)
        log_redaction = True
        compression = Compression.IN
        compression_min_size = 10
        compression_min_ratio = 11.0
        dns_nameserver = "dns_nameserver"
        dns_port = 8080
        disable_mozilla_ca_certificates = True
        dump_configuration = True
        opts = CouchbaseClusterOptions(
            # timeout_options
            bootstrap_timeout=bootstrap_timeout,
            resolve_timeout=resolve_timeout,
            connect_timeout=connect_timeout,
            kv_timeout=kv_timeout,
            kv_durable_timeout=kv_durable_timeout,
            views_timeout=views_timeout,
            query_timeout=query_timeout,
            analytics_timeout=analytics_timeout,
            search_timeout=search_timeout,
            management_timeout=management_timeout,
            dns_srv_timeout=dns_srv_timeout,
            idle_http_connection_timeout=idle_http_connection_timeout,
            config_idle_redial_timeout=config_idle_redial_timeout,
            config_total_timeout=config_total_timeout,
            # timeout_options
            # tracing_options
            tracing_threshold_kv=tracing_threshold_kv,
            tracing_threshold_view=tracing_threshold_view,
            tracing_threshold_query=tracing_threshold_query,
            tracing_threshold_search=tracing_threshold_search,
            tracing_threshold_analytics=tracing_threshold_analytics,
            tracing_threshold_eventing=tracing_threshold_eventing,
            tracing_threshold_management=tracing_threshold_management,
            tracing_threshold_queue_size=tracing_threshold_queue_size,
            tracing_threshold_queue_flush_interval=tracing_threshold_queue_flush_interval,
            tracing_orphaned_queue_size=tracing_orphaned_queue_size,
            tracing_orphaned_queue_flush_interval=tracing_orphaned_queue_flush_interval,
            # tracing_options
            enable_tls=enable_tls,
            enable_mutation_tokens=enable_mutation_tokens,
            enable_tcp_keep_alive=enable_tcp_keep_alive,
            ip_protocol=ip_protocol,
            enable_dns_srv=enable_dns_srv,
            show_queries=show_queries,
            enable_unordered_execution=enable_unordered_execution,
            enable_clustermap_notification=enable_clustermap_notification,
            enable_compression=enable_compression,
            enable_tracing=enable_tracing,
            enable_metrics=enable_metrics,
            network=network,
            tls_verify=tls_verify,
            tcp_keep_alive_interval=tcp_keep_alive_interval,
            config_poll_interval=config_poll_interval,
            config_poll_floor=config_poll_floor,
            max_http_connections=max_http_connections,
            user_agent_extra=user_agent_extra,
            logging_meter_emit_interval=logging_meter_emit_interval,
            log_redaction=log_redaction,
            compression=compression,
            compression_min_size=compression_min_size,
            compression_min_ratio=compression_min_ratio,
            dns_nameserver=dns_nameserver,
            dns_port=dns_port,
            disable_mozilla_ca_certificates=disable_mozilla_ca_certificates,
            dump_configuration=dump_configuration,
        )
        opt_dict = opts.to_dict()
        # print(opt_dict)
        opt_frm_dict = CouchbaseClusterOptions.from_dict(opt_dict)
        assert_output(opt_frm_dict)
        cb_cluster_opts = opts.get_cluster_options(auth=PasswordAuthenticator(username="username", password="password"))
        assert_output(cb_cluster_opts)
        cb_cluster_opts = opt_frm_dict.get_cluster_options(auth=PasswordAuthenticator(username="username", password="password"))
        assert_output(cb_cluster_opts)
