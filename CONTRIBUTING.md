# Contributing to Mood Detector

Thank you for your interest in contributing to Mood Detector! We welcome contributions from the community.

## How to Contribute

### Reporting Issues
- Use the issue tracker to report bugs or suggest features
- Describe what you were trying to do, what happened, and what you expected to happen
- Include information about your environment (OS, Python version, etc.)
- If possible, include a minimal example that reproduces the issue

### Pull Requests
1. Fork the repository
2. Create a new branch for your feature or bug fix
3. Make your changes with clear, descriptive commit messages
4. Add or update tests as needed
5. Update documentation if you're changing functionality
6. Submit a pull request with a clear description of your changes

## Development Setup

1. Clone your fork:
```bash
git clone https://github.com/YOUR_USERNAME/mood-detector
cd mood-detector
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install in development mode:
```bash
pip install -e .
pip install -r requirements.txt  # Install dev dependencies
```

4. Run tests:
```bash
python -m pytest tests/
```

## Code Style

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write clear, descriptive names for functions and variables
- Add docstrings for public functions and classes
- Keep functions focused on a single responsibility

## Testing

- Add unit tests for new functionality
- Ensure all tests pass before submitting a PR
- Test edge cases and error conditions
- Use pytest for writing tests

## Documentation

- Update docstrings when changing function behavior
- Update README.md if changing user-facing functionality
- Add/update examples in the examples/ directory
- Update API documentation in docs/ if adding new endpoints

## Project Structure

- `mood_detector/` - Core Python package
- `api/` - FastAPI application
- `cli/` - Command-line interface
- `examples/` - Usage examples
- `tests/` - Unit tests
- `docs/` - Documentation

## Getting Help

- Open an issue for technical questions
- Check existing issues and pull requests for similar work
- Be patient - maintainers have limited time

Thank you for contributing!