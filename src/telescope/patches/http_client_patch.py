import logging
import time

from ..entry_type import EntryType
from ..recorder import Recorder

logger = logging.getLogger("telescope.patches")

_original_requests_send = None
_original_httpx_send = None


def patch_http_clients():
    _patch_requests()
    _patch_httpx()


def _patch_requests():
    global _original_requests_send
    try:
        import requests

        _original_requests_send = requests.Session.send
        requests.Session.send = _patched_requests_send
    except ImportError:
        logger.debug("requests not installed")


def _patch_httpx():
    global _original_httpx_send
    try:
        import httpx

        _original_httpx_send = httpx.Client.send
        httpx.Client.send = _patched_httpx_send
    except ImportError:
        logger.debug("httpx not installed")


def _patched_requests_send(self, request, **kwargs):
    start = time.perf_counter()
    response = _original_requests_send(self, request, **kwargs)
    duration_ms = (time.perf_counter() - start) * 1000

    tags = [f"status:{response.status_code}", f"method:{request.method}"]
    if response.status_code >= 400:
        tags.append("error")

    content = {
        "method": request.method,
        "url": str(request.url),
        "status_code": response.status_code,
        "duration": round(duration_ms, 2),
        "request_headers": dict(request.headers),
        "response_headers": dict(response.headers),
        "response_size": len(response.content) if response.content else 0,
    }

    Recorder.record(entry_type=EntryType.CLIENT_REQUEST, content=content, tags=tags)
    return response


def _patched_httpx_send(self, request, **kwargs):
    start = time.perf_counter()
    response = _original_httpx_send(self, request, **kwargs)
    duration_ms = (time.perf_counter() - start) * 1000

    tags = [f"status:{response.status_code}", f"method:{request.method}"]
    if response.status_code >= 400:
        tags.append("error")

    content = {
        "method": str(request.method),
        "url": str(request.url),
        "status_code": response.status_code,
        "duration": round(duration_ms, 2),
        "request_headers": dict(request.headers),
        "response_headers": dict(response.headers),
    }

    Recorder.record(entry_type=EntryType.CLIENT_REQUEST, content=content, tags=tags)
    return response
