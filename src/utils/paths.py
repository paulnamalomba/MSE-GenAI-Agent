from __future__ import annotations
from pathlib import Path
from ..config import settings

BASE = Path(settings.data_dir)
FINANCIALS_BASE = Path(settings.financials_dir)


def ensure_dir(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p


def company_financials_dir(company: str) -> Path:
    safe = "".join(ch for ch in company if ch.isalnum() or ch in ("-","_"," ")).strip()
    d = FINANCIALS_BASE / safe
    return ensure_dir(d)
