# Changelog

All notable changes to cdli-cli will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-01-16

### Added

#### Core Functionality
- Complete CDLI REST API client with support for all documented endpoints
- Typer-based CLI with rich terminal formatting
- Full Python API for programmatic access
- Comprehensive error handling with specific exception types
- Support for content negotiation across all CDLI formats

#### Search Features
- Basic keyword search across all fields (`cdli find`)
- Advanced search with field filters (period, language, genre, etc.)
- URL ID query for batch fetching by P/Q/S numbers
- Pagination support for all search operations

#### Entity Operations
- Get operations for all entity types (tablets, publications, collections, etc.)
- List operations for metadata entities (periods, languages, genres, collections, provenances)
- Support for 9 different entity types

#### Image Downloads
- High-resolution photograph downloads
- Lineart (hand-drawn tracing) downloads
- Thumbnail versions for both image types
- Batch download (photo + lineart) with single command
- Automatic P-number prefix handling

#### Data Formats
- **Metadata:** JSON, JSON-LD, RDF/XML, Turtle, N-Triples
- **Inscriptions:** C-ATF, CDLI-CoNLL, CoNLL-U
- **Bibliography:** BibTeX, RIS, CSL-JSON, Formatted (with CSL styles)
- **Tabular:** CSV, TSV, Excel (XLSX)

#### Export Features
- Tablet export in multiple tabular formats
- Publication export
- Artifact-publication relationship export
- Pagination support for large datasets

#### CLI Features
- Command shortcuts (`find`, `tablet`, `inscription`)
- Rich table formatting for list and search results
- File output support with `--output` flag
- Custom base URL support for alternate CDLI instances
- Shell completion support

#### Python API
- Context manager support for automatic cleanup
- Full type hints for IDE autocomplete
- Pydantic models for data validation
- Comprehensive docstrings

#### Testing
- 22 unit tests with 100% pass rate
- pytest-httpx for HTTP mocking
- Comprehensive test coverage of core functionality
- Test fixtures for client setup

#### Documentation
- Comprehensive README with examples
- API coverage documentation mapping all endpoints
- Complete usage guide with practical examples
- Feature matrix documenting all capabilities
- Example scripts in Bash and Python
- Inline code documentation with docstrings

#### Error Handling
- NotFoundError for 404 responses
- APIError for HTTP error states
- Graceful handling of upstream API issues
- Clear error messages with status codes

### Known Issues (Upstream)

The following CDLI API endpoints return server errors (documented in GSoC 2020 API development report):

- `/search/advanced` - Returns 500 errors
- `/cdli-tablet/{P-number}` - Returns 500 errors for individual retrieval
- `/inscription/{id}` - Returns 500 errors
- `/artifacts` - Timeout issues

These are server-side issues, not client bugs. The search endpoint provides full artifact data as a workaround.

### Dependencies

- typer[all] >=0.9.0 - CLI framework
- httpx >=0.25.0 - HTTP client
- rich >=13.0.0 - Terminal formatting
- pydantic >=2.0.0 - Data validation

### Development Dependencies

- pytest >=7.0.0
- pytest-asyncio >=0.21.0
- pytest-httpx >=0.22.0
- ruff >=0.1.0
- mypy >=1.0.0

## [Unreleased]

### Planned
- PyPI publication
- Contributing guidelines
- CI/CD integration
- Performance benchmarks
- Additional export formats (Parquet, JSON Lines)
- ORACC integration for translations
- Async support for parallel downloads
- Local caching layer

---

[0.1.0]: https://github.com/cdli-cli/cdli-cli/releases/tag/v0.1.0