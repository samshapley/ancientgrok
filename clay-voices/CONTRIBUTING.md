# Contributing to ClayVoices

Thank you for your interest in contributing to ClayVoices! This project aims to advance the application of Large Language Models to ancient language translation.

## Ways to Contribute

### 1. Add New Models
- Implement clients for additional LLM providers
- Test newer model versions as they're released
- Optimize existing client implementations

### 2. Extend to Other Languages
- Adapt the framework for Akkadian, Hittite, or other cuneiform languages
- Test on Egyptian hieroglyphics or other ancient scripts
- Contribute parallel corpora for new language pairs

### 3. Improve Evaluation
- Add BERTScore and other semantic metrics
- Implement human evaluation frameworks
- Create qualitative analysis tools

### 4. Optimize Performance
- Experiment with prompt engineering strategies
- Test new few-shot selection methods
- Investigate fine-tuning vs in-context learning

### 5. Documentation & Testing
- Add more comprehensive tests
- Improve documentation
- Create tutorial notebooks
- Write usage examples

## Development Setup

```bash
# Clone the repository
git clone <repo-url>
cd clayvoices

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Set up API keys
cp .env.example .env  # Edit with your keys
```

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_data_loader.py -v
```

## Code Style

We follow PEP 8 with some modifications:

- Line length: 100 characters (not 79)
- Use type hints for all function signatures
- Docstrings: Google style
- Format code with Black before committing

```bash
# Format code
black src/ tests/

# Check style
flake8 src/ tests/

# Type checking
mypy src/
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add/update tests as needed
5. Ensure all tests pass
6. Update documentation
7. Commit with clear messages
8. Push to your fork
9. Open a Pull Request

## Experimental Protocol

When adding new experiments:

1. **Document hypothesis** - What are you testing?
2. **Use consistent seeds** - For reproducibility
3. **Save all results** - Including intermediate experiments
4. **Report costs** - Track API usage and expenses
5. **Create visualizations** - Learning curves, comparisons
6. **Update session docs** - Add to maestro/session_N.md

## Research Ethics

When working with ancient languages:

- Acknowledge source corpora (CDLI, ORACC, etc.)
- Credit original translators and Assyriologists
- Be transparent about model limitations
- Don't claim understanding beyond what's demonstrated
- Respect the academic context of the texts

## Questions?

Open an issue or reach out to the maintainers.

---

**License:** MIT - See LICENSE file for details