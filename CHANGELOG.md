# Changelog

All notable changes to the Task Manager App will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-11-18

### Added
- Initial stable release of MSE AI Agent

### Features
- ✅ Automated Data Scraping using Python OCR+NLP
- ✅ Structured Data Storage in Excel (.csv) format
- ✅ Quantitative Insights extraction (financial ratios, growth trends)
- ✅ Sentiment Analysis of CEO statements and news articles
- ✅ Fair Stock Price Estimation based on combined data
- ✅ Basic CLI for running scraper and exporting data
- ✅ Cross package use of `datashadric` for all complex data handling 

### Documentation
- 📖 **README.md:** Complete README with badges and quick start
- 📐 **docs/IDEA.md:** Architecture documentation with diagrams
- 🛠️ **docs/SETUP.md:** Setup guide with troubleshooting
- 📝 **CHANGELOG.md:** Changelog for version tracking

### Developer Experience
- `Python`:
  - Modular code structure for scraper, AI processing, and data export
  - Environment variable management with `python-dotenv`
  - Logging and error handling for robustness
- `GenAI`:
  - Integration with Gemini 2.5 Flash for NLP tasks `google-generativeai` package
  - API Keys stored either as system environment variables or in `.env` file
    - `GEMINI_API_KEY`
  - Prompt engineering for table extraction and sentiment analysis
- `GitHub`:
  - Repository with version control and issue tracking
  - Contribution guidelines in `docs/DEVELOPMENT.md`

### Core Cross-Package Dependencies

- `requests` + `BeautifulSoup4` for web scraping
- `pytesseract` + `Pillow` for OCR text extraction from PDFs
- `google-generativeai` for GenAI NLP tasks
- `pandas` for data manipulation and Excel exports
- `psycopg` for PostgreSQL database integration (future)
- `python-dotenv` for environment variable management
- `datashadric` for complex data handling across packages

---

## Future Enhancements

### Planned for v0.1.1
- [ ] Improved error handling and logging
- [ ] Enhanced prompt engineering for better data extraction accuracy
- [ ] Unit tests for core modules
- [ ] Developer documentation enhancements for easier onboarding and contribution

### Planned for v0.1.2
- [ ] PostgreSQL integration for structured data storage
- [ ] Advanced financial analysis metrics

### Planned for v0.2.0
- [ ] Docker containerization for easier deployment
- [ ] UI/UX implementation (desktop app)
- [ ] Power tools for bulk task management
- [ ] Report generation (PDF/Excel)

TBA

---

## Version History

- **v0.1.0** (2025-11-18) - First development release

---
<!-- 
## Contributing

See [DEVELOPMENT.md](./docs/DEVELOPMENT.md) for contribution guidelines. -->

## License

This project is licensed under the MIT License - see [LICENSE](./LICENSE) file for details.
