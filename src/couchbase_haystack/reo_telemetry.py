import threading
from importlib.metadata import version

def _send_telemetry() -> None:
    try:
        from reo_census import ReoEventLogger

        _pkg_version = version("couchbase-haystack")
        _logger = ReoEventLogger(
            endpoint_url="https://telemetry.reo.dev/data",
            timeout=3.0,
            package_name="couchbase-haystack",
            package_version=_pkg_version,
        )
        _logger.log_event()
    except Exception:
        pass

try:
    threading.Thread(target=_send_telemetry, daemon=True).start()
except Exception:
    pass