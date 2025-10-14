from __future__ import annotations
from pathlib import Path
import pandas as pd

def write_financials_manifest(records: list[dict], out_path: Path) -> Path:
    df = pd.DataFrame.from_records(records)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="financials")
    return out_path
