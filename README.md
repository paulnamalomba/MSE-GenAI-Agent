# MSE AI Agent

**Updated**: November 18, 2025<br>
**Author**: Paul Namalomba<br>
  - SESKA Computational Engineer<br>
  - Software Developer<br>
  - PhD Candidate (Civil Engineering Spec. Computational and Applied Mechanics)<br>
**Contact**: [kabwenzenamalomba@gmail.com](mailto:kabwenzenamalomba@gmail.com)

---

Automated scraping and analysis pipeline for Malawi Stock Exchange financial documents from `mse.co.mw`. It is an AI-powered agent that extracts financial data from PDFs, analyzes CEO statements, and provides structured data outputs for investor insights.

I have designed it to monitor, collect, and interpret financial data from the **Malawi Stock Exchange (MSE)**. The agent will automate the process of **scraping financial PDFs**, **storing structured data**, and **analyzing both quantitative and qualitative indicators** to estimate a company's fair stock price and future performance trends.

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

- **Scraper:** 
  - requests+BeautifulSoup4 for HTML scraping.
  - OCR + Tesseract for PDF text extraction.
  - respects robots.txt and rate limiting.
- **AI Agent:** 
  - GENAI Gemini 2.5 Flash.
  - Extracts tables, CEO statements, KPIs.
- **Storage:**
  - Initial version uses excel (.csv) exports.
  - Pandas for Excel exports and data manipulation.
  - Later: PostgreSQL for structured data.

---

**Current Version**: v0.1.0 (Nov 18 2025)<br>

*Check CHANGELOG.md for updates.*