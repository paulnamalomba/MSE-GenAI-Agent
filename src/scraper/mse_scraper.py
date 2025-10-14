from __future__ import annotations
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pathlib import Path
import re

from ..config import settings
from ..utils.http import http_get
from ..utils.paths import company_financials_dir

LISTINGS_URL = urljoin(settings.base_url, "markets/")


def parse_companies_from_listings(html: str) -> list[tuple[str, str]]:
    """
    Parse company names and URLs from the listings HTML.
    Expects rows with <a href="/company/..."> NAME</a>.
    Returns list of (name, company_url).
    """
    soup = BeautifulSoup(html, "html.parser")
    companies: list[tuple[str,str]] = []
    for a in soup.select("a[href^='/company/'], a[href*='/company/']"):
        name = a.get_text(strip=True)
        href = a.get("href")
        if not href or not name:
            continue
        # ignore nav items that are not tickers by filtering common known anchors
        if len(name) > 30:
            continue
        url = urljoin(settings.base_url, str(href))
        companies.append((name, url))
    # de-duplicate while preserving order
    seen = set()
    uniq: list[tuple[str,str]] = []
    for name, url in companies:
        key = (name, url)
        if key in seen:
            continue
        seen.add(key)
        uniq.append((name, url))
    return uniq


def find_financials_url(company_page_html: str, company_url: str) -> str | None:
    """
    Find the "Financials" nav link (vav-link or anchor with text 'Financials').
    """
    soup = BeautifulSoup(company_page_html, "html.parser")
    # Try by anchor text first
    for a in soup.find_all("a"):
        text = a.get_text(strip=True).lower()
        if "financials" in text:
            href = a.get("href")
            if href:
                return urljoin(company_url, str(href))
    # Try class-based selectors as fallback
    link = soup.select_one("a.vav-link[href*='financial']")
    if link and link.get("href"):
        return urljoin(company_url, str(link.get("href")))
    return None


def extract_financial_pdf_links(html: str, page_url: str) -> list[tuple[str,str]]:
    """
    Collect (label, pdf_url) for buttons with class 'btn btn-success' or direct anchors to PDFs.
    """
    soup = BeautifulSoup(html, "html.parser")
    results: list[tuple[str,str]] = []
    # Buttons with success class
    for a in soup.select("a.btn.btn-success"):
        label = a.get_text(strip=True) or "financial"
        href = a.get("href")
        if href:
            url = urljoin(page_url, str(href))
            results.append((label, url))
    # Any direct links to .pdf
    for a in soup.select("a[href$='.pdf'], a[href*='.pdf']"):
        label = a.get_text(strip=True) or "financial"
        href = a.get("href")
        if href:
            url = urljoin(page_url, str(href))
            results.append((label, url))
    # de-dup by url
    seen = set()
    uniq: list[tuple[str,str]] = []
    for label, url in results:
        if url in seen:
            continue
        seen.add(url)
        uniq.append((label, url))
    return uniq


def download_pdf(url: str, dest_dir: Path, label: str | None = None) -> Path | None:
    try:
        resp = http_get(url)
        filename = url.split("/")[-1]
        # optional: prepend label for readability if it's not already in name
        if label and label.lower() not in filename.lower():
            filename = f"{label.replace(' ','_')}_{filename}"
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / filename
        with open(dest, "wb") as f:
            f.write(resp.content)
        return dest
    except Exception as e:
        print(f"failed to download {url}: {e}")
        return None


def scrape_company_financials(name: str, url: str) -> list[Path]:
    print(f"Scraping company: {name} -> {url}")
    page = http_get(url)
    fin_url = find_financials_url(page.text, url)
    if not fin_url:
        print(f"  Financials link not found for {name}")
        return []
    fin_page = http_get(fin_url)
    pdfs = extract_financial_pdf_links(fin_page.text, fin_url)
    if not pdfs:
        print(f"  No financial PDFs found for {name}")
        return []
    out_dir = company_financials_dir(name)
    saved = []
    for label, pdf_url in pdfs:
        p = download_pdf(pdf_url, out_dir, label)
        if p:
            print(f"  saved: {p}")
            saved.append(p)
    return saved


def scrape_all_companies(listings_url: str = LISTINGS_URL) -> dict[str, list[Path]]:
    resp = http_get(listings_url)
    companies = parse_companies_from_listings(resp.text)
    print(f"Found {len(companies)} companies on listings page")
    results: dict[str, list[Path]] = {}
    for name, url in companies:
        results[name] = scrape_company_financials(name, url)
    return results


if __name__ == "__main__":
    # Simple demo: find one company from listings and scrape its financials
    print("Demo: scraping a single company to verify the pipeline")
    try:
        resp = http_get(LISTINGS_URL)
        companies = parse_companies_from_listings(resp.text)
        print(f"Discovered {len(companies)} companies on listings page")
        preferred = None
        # Prefer AIRTEL if present, otherwise first company
        for name, url in companies:
            if name.upper().startswith("AIRTEL"):
                preferred = (name, url)
                break
        if preferred is None and companies:
            preferred = companies[0]
        if not preferred:
            print("No companies found on the listings page.")
        else:
            name, url = preferred
            print(f"Testing with company: {name}")
            saved = scrape_company_financials(name, url)
            if saved:
                print("Downloaded files:")
                for p in saved:
                    print(f" - {p}")
            else:
                print("No files downloaded for the test company.")
    except Exception as e:
        print(f"Demo failed: {e}")
