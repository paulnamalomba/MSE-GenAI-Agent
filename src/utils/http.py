from __future__ import annotations

import time
from contextlib import contextmanager
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Optional, Dict, Any, cast

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

try:  # pragma: no cover - optional dependency
    import requests_cache  # type: ignore[import]
except ImportError:  # pragma: no cover - optional dependency
    requests_cache = None  # type: ignore[assignment]

from ..config import settings
from .http_state import prepare_conditional_headers, update_metadata

_session: Optional[requests.Session] = None


def _parse_retry_after(value: Optional[str]) -> Optional[float]:
    if not value:
        return None
    value = value.strip()
    if not value:
        return None
    if value.isdigit():
        return max(0.0, float(value))
    try:
        dt = parsedate_to_datetime(value)
        if dt is None:
            return None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        delay = (dt - datetime.now(timezone.utc)).total_seconds()
        return max(0.0, delay)
    except Exception:
        return None


@contextmanager
def _maybe_disable_cache(session: requests.Session, cacheable: bool):
    session_any = cast(Any, session)
    if cacheable or not hasattr(session_any, "cache_disabled"):
        yield
    else:
        with session_any.cache_disabled():
            yield


def get_session() -> requests.Session:
    global _session
    if _session is None:
        if requests_cache is not None:
            s = requests_cache.CachedSession(
                cache_name=settings.http_cache_path,
                backend="sqlite",
                expire_after=settings.http_cache_expire,
                allowable_methods=("GET", "HEAD"),
                cache_control=True,
            )
        else:
            s = requests.Session()

        retries = Retry(
            total=settings.retries,
            backoff_factor=settings.backoff,
            status_forcelist=(500, 502, 503, 504),
            allowed_methods=("GET", "HEAD"),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retries)
        s.mount("http://", adapter)
        s.mount("https://", adapter)
        s.headers.update(
            {
                "User-Agent": settings.user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
        )
        _session = s
    return _session


def http_request(
    method: str,
    url: str,
    *,
    timeout: int | float | None = None,
    headers: Optional[Dict[str, str]] = None,
    stream: bool = False,
    conditional: bool = True,
    cacheable: bool = True,
) -> requests.Response:
    session = get_session()
    request_headers: Dict[str, str] = {}
    if headers:
        request_headers.update(headers)

    method_upper = method.upper()
    if conditional and method_upper in {"GET", "HEAD"}:
        request_headers.update(prepare_conditional_headers(url))

    attempts = 0
    while True:
        with _maybe_disable_cache(session, cacheable):
            resp = session.request(
                method_upper,
                url,
                timeout=timeout or settings.timeout,
                headers=request_headers,
                stream=stream,
            )

        if resp.status_code in {429, 503}:
            retry_after = _parse_retry_after(resp.headers.get("Retry-After"))
            if (
                retry_after is not None
                and attempts < settings.retry_after_max_attempts
            ):
                sleep_for = max(retry_after, settings.retry_after_floor)
                time.sleep(sleep_for)
                attempts += 1
                continue

        break

    if conditional and method_upper in {"GET", "HEAD"} and resp.status_code == 200:
        update_metadata(url, dict(resp.headers))

    resp.raise_for_status()
    return resp


def http_get(
    url: str,
    *,
    timeout: int | float | None = None,
    headers: Optional[Dict[str, str]] = None,
    stream: bool = False,
    conditional: bool = True,
    cacheable: bool = True,
) -> requests.Response:
    return http_request(
        "GET",
        url,
        timeout=timeout,
        headers=headers,
        stream=stream,
        conditional=conditional,
        cacheable=cacheable,
    )


def http_head(
    url: str,
    *,
    timeout: int | float | None = None,
    headers: Optional[Dict[str, str]] = None,
    conditional: bool = True,
    cacheable: bool = True,
) -> requests.Response:
    return http_request(
        "HEAD",
        url,
        timeout=timeout,
        headers=headers,
        conditional=conditional,
        cacheable=cacheable,
    )
