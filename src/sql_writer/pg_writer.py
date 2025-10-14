from __future__ import annotations
from dataclasses import dataclass
import os
import psycopg2

@dataclass
class FileMeta:
    company: str
    label: str
    url: str
    path: str


def upsert_file_meta(conn_str: str, items: list[FileMeta]):
    if not conn_str:
        print("No POSTGRES_DSN provided; skipping DB write.")
        return
    conn = psycopg2.connect(conn_str)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS financial_files (
                    company TEXT,
                    label TEXT,
                    url TEXT PRIMARY KEY,
                    path TEXT
                );
                """
            )
            for it in items:
                cur.execute(
                    """
                    INSERT INTO financial_files (company, label, url, path)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (url) DO UPDATE SET
                        company = EXCLUDED.company,
                        label = EXCLUDED.label,
                        path = EXCLUDED.path;
                    """,
                    (it.company, it.label, it.url, it.path),
                )
        conn.commit()
    finally:
        conn.close()
