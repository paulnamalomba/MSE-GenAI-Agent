# MSE AI Agent

Automated scraping and analysis pipeline for Malawi Stock Exchange financial documents.

## Structure

- src/
  - scraper/
  - processing_ai/
  - excel_writer/
  - sql_writer/
  - utils/
- data/
  - financials/{COMPANY}/

## Quick start

1. Copy .env.example to .env and fill values.
2. Install requirements.
3. Run scraper.

## Notes

- Scraper: requests+BeautifulSoup; respects robots.txt and rate limiting.
- AI: Gemini 2.5 Flash (planned) for later processing modules.
