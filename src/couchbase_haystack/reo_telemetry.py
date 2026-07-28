from importlib.metadata import version

try:
    from reo_census import ReoEventLogger

    _pkg_version = version("couchbase-haystack")
    _logger = ReoEventLogger(
        endpoint_url="https://telemetry.reo.dev/data",
        timeout=3.0,
        package_name="couchbase-haystack",
        package_version=_pkg_version,
    )
    _logger.log_event({"activity_type": "package_import"})
except Exception:  # noqa: S110
    pass
