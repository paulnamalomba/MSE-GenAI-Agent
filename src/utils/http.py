from __future__ import annotations
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Optional
from ..config import settings

_session: Optional[requests.Session] = None

def get_session() -> requests.Session:
    global _session
    if _session is None:
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
        s.headers.update({
            "User-Agent": settings.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        })
        _session = s
    return _session


def http_get(url: str, timeout: int | float | None = None) -> requests.Response:
    s = get_session()
    resp = s.get(url, timeout=timeout or settings.timeout)
    resp.raise_for_status()
    return resp
