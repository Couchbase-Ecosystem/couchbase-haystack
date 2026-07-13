from importlib.metadata import version

try:
    from reo_census import ReoEventLogger

    _pkg_version = version("couchbase-haystack")  # falls back to "0.0.0"
    _logger = ReoEventLogger(
        endpoint_url="https://telemetry.reo.dev/data",
        timeout=3.0,
        package_name="couchbase-haystack",
        package_version=_pkg_version,
    )
    _logger.log_event()
except Exception:
    pass
