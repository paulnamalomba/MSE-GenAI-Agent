from __future__ import annotations

import hashlib
import random
import time
from pathlib import Path
from typing import Optional
import re

from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser

from ..config import settings
from ..utils.http import http_get
from ..utils.http_state import update_metadata
from ..utils.paths import company_financials_dir, ensure_dir

LISTINGS_URL = urljoin(settings.base_url, "market/mainboard")
HTML_CACHE_DIR = ensure_dir(Path(settings.data_dir) / "html-cache")


def _load_robot_rules() -> tuple[Optional[RobotFileParser], Optional[float]]:
    robots_url = urljoin(settings.base_url, "robots.txt")
    parser = RobotFileParser()
    try:
        parser.set_url(robots_url)
        parser.read()
        raw_delay = parser.crawl_delay(settings.user_agent) or parser.crawl_delay("*")
        delay: Optional[float]
        if raw_delay is None:
            delay = None
        elif isinstance(raw_delay, (int, float)):
            delay = float(raw_delay)
        else:
            try:
                delay = float(raw_delay)
            except (TypeError, ValueError):
                delay = None
        if delay is not None and delay < 0:
            delay = None
        return parser, delay
    except Exception as err:
        print(f"warning: unable to load robots.txt ({err})")
        return None, None


ROBOT_PARSER, ROBOT_CRAWL_DELAY = _load_robot_rules()


def _sleep_with_jitter(low: float, high: float) -> None:
    minimum = ROBOT_CRAWL_DELAY or 0.0
    delay = random.uniform(low, high)
    time.sleep(max(delay, minimum))


def _allowed(url: str) -> bool:
    if ROBOT_PARSER is None:
        return True
    agent = settings.user_agent or "*"
    try:
        return ROBOT_PARSER.can_fetch(agent, url)
    except Exception:
        return True


def _html_cache_path(url: str) -> Path:
    try:
        digest = hashlib.sha1(url.encode("utf-8"), usedforsecurity=False).hexdigest()
    except TypeError:  # pragma: no cover - older OpenSSL
        digest = hashlib.sha1(url.encode("utf-8")).hexdigest()
    return HTML_CACHE_DIR / f"{digest}.html"


def _store_html(url: str, text: str) -> None:
    path = _html_cache_path(url)
    with path.open("w", encoding="utf-8") as handle:
        handle.write(text)


def _load_html(url: str) -> Optional[str]:
    path = _html_cache_path(url)
    if path.exists():
        try:
            return path.read_text(encoding="utf-8")
        except Exception:
            return None
    return None


def fetch_html(url: str, label: str) -> Optional[str]:
    if not _allowed(url):
        print(f"  robots.txt disallows fetching {label}: {url}")
        return None

    resp = http_get(url, cacheable=True, conditional=True)
    from_cache = getattr(resp, "from_cache", False)

    if resp.status_code == 304:
        cached = _load_html(url)
        resp.close()
        if cached is not None:
            if not from_cache:
                _sleep_with_jitter(8, 15)
            return cached
        # fallback: fetch without conditional headers to refresh local cache
        resp = http_get(url, cacheable=True, conditional=False)
        from_cache = getattr(resp, "from_cache", False)

    text = resp.text
    _store_html(url, text)
    resp.close()
    if not from_cache:
        _sleep_with_jitter(8, 15)
    return text

def _sanitize_label(label: str) -> str:
    cleaned = re.sub(r"[^\w\-]+", "_", label.strip())
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    return cleaned or "financial"


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



def extract_financial_pdf_links(html: str, page_url: str) -> list[tuple[str, str]]:
    """
    Collect (label, pdf_url) pairs using the row's `sorting_1` cell when available.
    """
    soup = BeautifulSoup(html, "html.parser")
    results: list[tuple[str, str]] = []

    for row in soup.select("tr"):
        row_label = None
        sorting_cell = row.select_one(".sorting_1")
        if sorting_cell:
            row_label = sorting_cell.get_text(strip=True)

        anchors = row.select("a[href$='.pdf'], a[href*='.pdf'], a.btn.btn-success[href]")
        for a in anchors:
            href = a.get("href")
            if not href:
                continue
            label = row_label or a.get_text(strip=True) or "financial"
            results.append((label, urljoin(page_url, str(href))))

    seen = set()
    uniq: list[tuple[str, str]] = []
    for label, url in results:
        if url in seen:
            continue
        seen.add(url)
        uniq.append((label, url))
    return uniq


def download_pdf(url: str, dest_dir: Path, label: str | None = None) -> Path | None:
    if not _allowed(url):
        print(f"    skipping {url} (disallowed by robots.txt)")
        return None

    try:
        resp = http_get(url, stream=True, conditional=True, cacheable=False)
        from_cache = getattr(resp, "from_cache", False)
        conditional = True

        filename = url.split("/")[-1]
        if label:
            prefix = _sanitize_label(label)
            if prefix and prefix.lower() not in filename.lower():
                filename = f"{prefix}_{filename}"

        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / filename

        if resp.status_code == 304:
            resp.close()
            if dest.exists():
                print(f"    unchanged: {dest.name}")
                return dest
            conditional = False
            resp = http_get(url, stream=True, conditional=False, cacheable=False)
            from_cache = getattr(resp, "from_cache", False)

        if resp.status_code != 200:
            print(f"    unexpected status {resp.status_code} for {url}")
            resp.close()
            return None

        with dest.open("wb") as handle:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    handle.write(chunk)
        headers_dict = dict(resp.headers)
        resp.close()

        if not conditional:
            update_metadata(url, headers_dict)

        if not from_cache:
            _sleep_with_jitter(5, 12)

        return dest
    except Exception as e:
        print(f"failed to download {url}: {e}")
        return None


def scrape_company_financials(name: str, url: str) -> list[Path]:
    print(f"Scraping company: {name} -> {url}")
    print("  fetching company page...")
    page_html = fetch_html(url, f"company page for {name}")
    if page_html is None:
        print(f"  unable to fetch company page for {name}")
        return []

    print("  locating financials link...")
    fin_url = find_financials_url(page_html, url)
    if not fin_url:
        print(f"  Financials link not found for {name}")
        return []
    print(f"  fetching financials page: {fin_url} ...")
    fin_html = fetch_html(fin_url, f"financials page for {name}")
    if fin_html is None:
        print(f"  unable to fetch financials page for {name}")
        return []

    print("  extracting financial PDF links...")
    pdfs = extract_financial_pdf_links(fin_html, fin_url)
    if not pdfs:
        print(f"  No financial PDFs found for {name}")
        return []
    print(f"  found {len(pdfs)} PDF(s); downloading...")
    for label, pdf_url in pdfs:
        print(f"    - {label}: {pdf_url}")
    out_dir = company_financials_dir(name)
    saved: list[Path] = []
    for label, pdf_url in pdfs:
        path = download_pdf(pdf_url, out_dir, label)
        if path:
            print(f"  saved: {path}")
            saved.append(path)
    return saved


def scrape_all_companies(listings_url: str = LISTINGS_URL) -> dict[str, list[Path]]:
    listings_html = fetch_html(listings_url, "listings page")
    if listings_html is None:
        print(f"Unable to fetch listings page: {listings_url}")
        return {}
    companies = parse_companies_from_listings(listings_html)
    print(f"Found {len(companies)} companies on listings page")
    results: dict[str, list[Path]] = {}
    for name, url in companies:
        results[name] = scrape_company_financials(name, url)
    return results


if __name__ == "__main__":
    # Simple demo: find one company from listings and scrape its financials
    print("Demo: scraping a single company to verify the pipeline")
    try:
        listings_html = fetch_html(LISTINGS_URL, "listings page")
        if listings_html is None:
            raise RuntimeError("Unable to load listings page for demo")
        companies = parse_companies_from_listings(listings_html)
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
            print(f"Testing with company: {name}", f"-> {url}")
            saved = scrape_company_financials(name, url)
            if saved:
                print("Downloaded files:")
                for p in saved:
                    print(f" - {p}")
            else:
                print("No files downloaded for the test company.")
    except Exception as e:
        print(f"Demo failed: {e}")
