# Contributing to CDLI CLI

Thank you for your interest in contributing to cdli-cli! This document provides guidelines and instructions for contributing.

## Development Setup

1. **Fork and clone the repository:**
```bash
git clone https://github.com/your-username/cdli-cli.git
cd cdli-cli
```

2. **Install in development mode:**
```bash
pip install -e '.[dev]'
```

3. **Run tests:**
```bash
pytest -v
```

## Code Standards

### Python Version
- Minimum: Python 3.9
- Target: Python 3.12

### Code Style
- Use Ruff for linting and formatting
- Follow PEP 8 guidelines
- Maximum line length: 100 characters
- Use type hints for all functions

### Type Checking
- Run mypy for type checking
- Ensure full type hint coverage
- Use Pydantic for data models

## Testing

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=cdli_cli --cov-report=html

# Run specific test
pytest tests/test_client.py::test_search -v
```

### Writing Tests
- Place tests in `tests/` directory
- Use pytest fixtures for common setup
- Mock HTTP requests with pytest-httpx
- Test both success and error cases
- Aim for >80% code coverage

### Test Structure
```python
def test_feature_name(httpx_mock: HTTPXMock, client):
    """Test description."""
    # Arrange
    httpx_mock.add_response(url="...", json={...})
    
    # Act
    result = client.method()
    
    # Assert
    assert result == expected
```

## Documentation

### Docstrings
- Use Google style docstrings
- Document all public functions and classes
- Include Args, Returns, and Raises sections
- Provide usage examples for complex functions

### README Updates
- Keep README.md synchronized with features
- Update examples when adding new commands
- Document any breaking changes

### API Documentation
- Update API_COVERAGE.md for new endpoints
- Update USAGE_GUIDE.md with new examples
- Update FEATURE_MATRIX.md when adding features

## Pull Request Process

1. **Create a feature branch:**
```bash
git checkout -b feature/your-feature-name
```

2. **Make your changes:**
- Write code following style guidelines
- Add tests for new functionality
- Update documentation
- Run tests locally

3. **Commit your changes:**
```bash
git add .
git commit -m "feat: add awesome feature"
```

Use conventional commit messages:
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `test:` - Test additions/changes
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks

4. **Push and create PR:**
```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub with:
- Clear description of changes
- Link to relevant issues
- Test results
- Documentation updates

5. **Code Review:**
- Address review feedback
- Keep PR scope focused
- Ensure CI checks pass

## Areas for Contribution

### High Priority
- Additional output formats (Parquet, JSON Lines)
- Performance improvements (async support, caching)
- ORACC integration for translations
- Interactive TUI mode

### Medium Priority
- More comprehensive error messages
- Progress bars for bulk operations
- Configuration file support
- Integration tests with live API

### Documentation
- Additional usage examples
- Tutorial videos/GIFs
- Translation to other languages
- API endpoint documentation improvements

### Testing
- Integration tests
- Performance benchmarks
- Edge case coverage
- Mock data generators

## Code of Conduct

### Our Pledge
We are committed to providing a welcoming and inclusive experience for all contributors.

### Expected Behavior
- Be respectful and considerate
- Welcome diverse perspectives
- Focus on constructive feedback
- Help others learn and grow

### Unacceptable Behavior
- Harassment or discrimination
- Trolling or inflammatory comments
- Personal attacks
- Publishing others' private information

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for questions or ideas
- Email maintainers for private inquiries

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Attribution

This project builds on the CDLI framework developed by the Cuneiform Digital Library Initiative.
We acknowledge the GSoC 2020 API development by Lars Willighagen and the CDLI team.