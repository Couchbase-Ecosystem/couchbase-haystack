"""
Package-level telemetry for couchbase-haystack using Scarf.

Sends a single, non-blocking telemetry ping when the package is first imported.
Respects DO_NOT_TRACK and SCARF_NO_ANALYTICS environment variables (handled by the Scarf SDK).
All errors are silently suppressed — telemetry must never interrupt the user.
"""

import platform
import threading
from contextlib import suppress
from importlib.metadata import version

SCARF_ENDPOINT_URL = "https://couchbase.gateway.scarf.sh/couchbase-haystack"

_telemetry_sent = threading.Event()
_telemetry_lock = threading.Lock()


def _get_package_version() -> str:
    """Return the installed package version, or 'unknown' if unavailable."""
    with suppress(Exception):
        return version("couchbase-haystack")
    return "unknown"


def _send_telemetry() -> None:
    """Send a single telemetry event to Scarf."""
    with _telemetry_lock:
        if _telemetry_sent.is_set():
            return
        _telemetry_sent.set()

    with suppress(Exception):
        from scarf import ScarfEventLogger  # noqa: PLC0415

        event_logger = ScarfEventLogger(
            endpoint_url=SCARF_ENDPOINT_URL,
            timeout=2.0,
        )

        event_logger.log_event(
            {
                "package": "couchbase-haystack",
                "version": _get_package_version(),
                "python_version": platform.python_version(),
                "os": platform.system(),
                "arch": platform.machine(),
            }
        )


def send_telemetry() -> None:
    """Fire-and-forget telemetry in a background daemon thread.

    Safe to call multiple times; only the first invocation actually sends.
    """
    with suppress(Exception):
        t = threading.Thread(target=_send_telemetry, daemon=True)
        t.start()
