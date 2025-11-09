# Contributing to WildGuard-Temporal

Thank you for your interest in contributing to WildGuard-Temporal! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Issues

- Use the GitHub issue tracker to report bugs
- Describe the issue in detail with steps to reproduce
- Include your Python version, OS, and relevant dependencies

### Suggesting Enhancements

- Open an issue describing the enhancement
- Explain why this enhancement would be useful
- Provide examples of how it would work

### Pull Requests

1. Fork the repository
2. Create a new branch for your feature (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest tests/`)
6. Format code with black (`black wildguard_temporal/`)
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## Development Setup

```bash
# Clone the repository
git clone https://github.com/nathanlubchenco/safety-bench.git
cd safety-bench

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with all dependencies
pip install -e ".[dev,viz]"

# Run tests
pytest tests/

# Run examples
python examples/basic_usage.py
```

## Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Write docstrings for all public functions and classes
- Keep functions focused and modular

## Testing

- Write tests for all new features
- Maintain test coverage above 80%
- Use pytest for testing
- Include both unit tests and integration tests

## Areas for Contribution

We welcome contributions in the following areas:

1. **New Scenario Types**
   - Additional temporal safety scenarios
   - Domain-specific scenarios
   - Multi-modal scenarios

2. **Evaluator Integrations**
   - Integration with LlamaGuard, ShieldGemma, etc.
   - Custom safety classifiers
   - Improved keyword-based evaluation

3. **Metrics and Analysis**
   - Additional safety metrics
   - Statistical analysis tools
   - Visualization improvements

4. **Documentation**
   - Tutorials and guides
   - Real-world case studies
   - API documentation improvements

5. **Testing and Quality**
   - Additional test coverage
   - Performance benchmarks
   - Bug fixes

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Maintain a professional environment

## Questions?

Feel free to open an issue for questions or reach out to the maintainers.

Thank you for contributing!
