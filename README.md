# MSE AI Agent

**Last updated**: December 04, 2025<br>
**Author**: [Paul Namalomba](https://github.com/paulnamalomba)<br>
  - SESKA Computational Engineer<br>
  - Software Developer<br>
  - PhD Candidate (Civil Engineering Spec. Computational and Applied Mechanics)<br>
**Version**: v0.1.1 (Dec 2025)<br>
**Contact**: [kabwenzenamalomba@gmail.com](kabwenzenamalomba@gmail.com)

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-1.3%2B-green.svg)](https://pandas.pydata.org/)
[![Google Gemini 3](https://img.shields.io/badge/Google-Gemini%203%Pro-orange.svg)](https://ai.google.dev/gemini-api/docs)
[![BeautifulSoup4](https://img.shields.io/badge/BeautifulSoup4-4.9%2B-yellow.svg)](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
[![License: MIT](https://img.shields.io/badge/License-MIT-gray.svg)](https://opensource.org/licenses/MIT)

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
  - Google Generative AI: Gemini 3 Pro.
  - Extracts tables, CEO statements, KPIs.
- **Storage:**
  - Initial version uses excel (.csv) exports.
  - Pandas for Excel exports and data manipulation.
  - Later: PostgreSQL for structured data.

---

**Current Version**: v0.1.0 (Nov 18 2025)<br>

*Check CHANGELOG.md for updates.*