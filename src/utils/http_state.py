from __future__ import annotations
import json
from pathlib import Path
from threading import RLock
from typing import Dict, Any

from ..config import settings

_STATE_LOCK = RLock()
_STATE_CACHE: Dict[str, Dict[str, Any]] | None = None


def _state_path() -> Path:
    path = Path(settings.http_state_path)
    if not path.is_absolute():
        path = Path(settings.http_state_path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _load_state() -> Dict[str, Dict[str, Any]]:
    global _STATE_CACHE
    with _STATE_LOCK:
        if _STATE_CACHE is None:
            path = _state_path()
            if path.exists():
                try:
                    with path.open("r", encoding="utf-8") as handle:
                        _STATE_CACHE = json.load(handle)
                except Exception:
                    _STATE_CACHE = {}
            else:
                _STATE_CACHE = {}
        assert _STATE_CACHE is not None
        return _STATE_CACHE


def _save_state() -> None:
    state = _load_state()
    path = _state_path()
    with _STATE_LOCK:
        with path.open("w", encoding="utf-8") as handle:
            json.dump(state, handle, indent=2, sort_keys=True)


def get_metadata(url: str) -> Dict[str, Any]:
    state = _load_state()
    return state.get(url, {})


def prepare_conditional_headers(url: str) -> Dict[str, str]:
    meta = get_metadata(url)
    headers: Dict[str, str] = {}
    etag = meta.get("etag")
    last_modified = meta.get("last_modified")
    if etag:
        headers["If-None-Match"] = etag
    if last_modified:
        headers["If-Modified-Since"] = last_modified
    return headers


def update_metadata(url: str, headers: Dict[str, Any]) -> None:
    etag = headers.get("ETag")
    last_modified = headers.get("Last-Modified")
    if not etag and not last_modified:
        return
    state = _load_state()
    state[url] = {
        "etag": etag,
        "last_modified": last_modified,
    }
    _save_state()


def clear_metadata(url: str) -> None:
    state = _load_state()
    if url in state:
        del state[url]
    _save_state()