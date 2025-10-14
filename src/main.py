from __future__ import annotations
from pathlib import Path
import argparse
import os

from .scraper.mse_scraper import scrape_all_companies, scrape_company_financials, LISTINGS_URL
from .excel_writer.manifest import write_financials_manifest
from .sql_writer.pg_writer import FileMeta, upsert_file_meta
from .config import settings


def main():
    parser = argparse.ArgumentParser(description="MSE Financials Scraper")
    parser.add_argument("--all", action="store_true", help="Scrape all companies from listings page")
    parser.add_argument("--company", action="append", help="Specific company name to scrape (can pass multiple)")
    parser.add_argument("--listings-url", default=LISTINGS_URL, help="Override listings URL")
    parser.add_argument("--manifest", default="./data/financials_manifest.xlsx", help="Path to write manifest excel")
    parser.add_argument("--write-db", action="store_true", help="Write file metadata to Postgres if DSN provided")
    parser.add_argument("--demo", action="store_true", help="Run a single-company demo (AIRTEL if available)")
    args = parser.parse_args()

    results: dict[str, list[Path]] = {}

    if args.demo:
        # Single-company demo: prefer AIRTEL, else first
        from .scraper.mse_scraper import parse_companies_from_listings, scrape_company_financials
        try:
            import sys
            from .utils.http import http_get
            resp = http_get(args.listings_url)
            companies = parse_companies_from_listings(resp.text)
            if not companies:
                print("No companies discovered on listings page; cannot run demo.")
                return
            preferred = None
            for name, url in companies:
                if name.upper().startswith("AIRTEL"):
                    preferred = (name, url)
                    break
            if preferred is None:
                preferred = companies[0]
            name, url = preferred
            print(f"Demo running for company: {name} -> {url}")
            paths = scrape_company_financials(name, url)
            results[name] = paths
        except Exception as e:
            print(f"Demo failed: {e}")
            return
    elif args.all:
        results = scrape_all_companies(args.listings_url)
    elif args.company:
        # Note: For company-specific scraping we need the mapping name->url. Here we re-scrape listings and filter.
        all_results = scrape_all_companies(args.listings_url)
        for name in args.company:
            if name in all_results:
                results[name] = all_results[name]
            else:
                print(f"Company '{name}' not found on listings page; skipping.")
    else:
        print("No action specified. Use --all or --company NAME")
        return

    # Build manifest records
    records = []
    filemetas = []
    for company, paths in results.items():
        for p in paths:
            records.append({
                "company": company,
                "file": p.name,
                "path": str(p),
            })
            filemetas.append(FileMeta(company=company, label=p.stem, url="", path=str(p)))

    if records:
        out = Path(args.manifest)
        write_financials_manifest(records, out)
        print(f"Manifest written: {out}")

    if args.write_db and filemetas:
        upsert_file_meta(os.getenv("POSTGRES_DSN", ""), filemetas)


if __name__ == "__main__":
    main()
