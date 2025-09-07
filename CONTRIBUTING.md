# Contributing to HLS Converter

Thank you for your interest in contributing to HLS Converter! This document provides guidelines and instructions for contributing to the project.

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- FFmpeg installed and available in PATH
- Git for version control

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/your-username/hls-converter.git
   cd hls-converter
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On macOS/Linux:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

## 🛠️ Development Workflow

### Code Style

We use several tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking

Format your code before committing:

```bash
# Format code
black hls_converter/
isort hls_converter/

# Check linting
flake8 hls_converter/

# Type checking
mypy hls_converter/
```

### Testing

Run the test suite to ensure your changes don't break existing functionality:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=hls_converter

# Run specific test file
pytest tests/test_converter.py

# Run with verbose output
pytest -v
```

### Writing Tests

Please add tests for new functionality. We use pytest for testing:

```python
# tests/test_new_feature.py
import pytest
from hls_converter import HLSConverter

def test_new_feature():
    converter = HLSConverter()
    result = converter.new_feature()
    assert result is not None
```

### Documentation

Update documentation for any new features or changes:

1. **Docstrings**: Use Google-style docstrings for all functions and classes
2. **README.md**: Update usage examples and feature descriptions
3. **Type hints**: Add type hints to all function parameters and return values

Example docstring:

```python
def convert_video(self, input_file: Path, output_dir: Path) -> Dict[str, Any]:
    \"\"\"
    Convert video to HLS format.
    
    Args:
        input_file: Path to the input video file
        output_dir: Directory to save HLS output
        
    Returns:
        Dictionary containing conversion results and metadata
        
    Raises:
        FileNotFoundError: If input file doesn't exist
        ValueError: If output directory cannot be created
    \"\"\"
```

## 📝 Making Changes

### Branch Naming

Use descriptive branch names:
- `feature/add-dash-support` - for new features
- `fix/memory-leak-issue` - for bug fixes
- `docs/update-readme` - for documentation updates
- `refactor/improve-performance` - for refactoring

### Commit Messages

Write clear, descriptive commit messages:

```
feat: add DASH streaming support

- Implement DASH manifest generation
- Add DASH-specific configuration options
- Update CLI with DASH output format option
- Add tests for DASH functionality

Closes #123
```

Use conventional commit prefixes:
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation updates
- `test:` - Test additions/updates
- `refactor:` - Code refactoring
- `perf:` - Performance improvements
- `style:` - Code style changes

### Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes and commit them**
   ```bash
   git add .
   git commit -m "feat: your descriptive message"
   ```

3. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Create a Pull Request**
   - Provide a clear title and description
   - Reference any related issues
   - Include examples of usage if applicable
   - Ensure all tests pass

### Pull Request Template

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or breaking changes documented)
```

## 🐛 Reporting Bugs

### Before Reporting

1. Check if the issue has already been reported
2. Try the latest version of the software
3. Test with minimal configuration to isolate the problem

### Bug Report Template

When reporting bugs, please include:

```markdown
**Bug Description**
A clear description of what the bug is.

**Steps to Reproduce**
1. Run command: `hls-converter input.mp4`
2. With configuration: `{}`
3. See error: `...`

**Expected Behavior**
What you expected to happen.

**Actual Behavior**
What actually happened.

**Environment**
- OS: [e.g., macOS 12.0]
- Python version: [e.g., 3.9.0]
- HLS Converter version: [e.g., 1.0.0]
- FFmpeg version: [e.g., 4.4.0]

**Additional Context**
- Configuration files used
- Input file characteristics
- Full error messages or logs
- Screenshots if applicable
```

## 💡 Suggesting Features

### Feature Request Template

```markdown
**Feature Description**
Clear description of the feature you'd like to see.

**Use Case**
Describe the problem this feature would solve.

**Proposed Solution**
How you think this should be implemented.

**Alternatives Considered**
Other approaches you've considered.

**Additional Context**
Any other context, mockups, or examples.
```

## 🏗️ Architecture Overview

Understanding the codebase structure:

```
hls_converter/
├── __init__.py          # Package initialization and exports
├── cli.py               # Command-line interface
├── converter.py         # Main HLSConverter class
├── config.py            # Configuration management
├── encoder_detector.py  # Hardware/software encoder detection
├── media_analyzer.py    # Media file analysis
└── processors.py        # Video/audio/subtitle processors
```

### Key Components

- **HLSConverter**: Main orchestrator class
- **MediaAnalyzer**: Analyzes input media characteristics
- **EncoderDetector**: Detects available encoders
- **Processors**: Handle specific media type processing
- **HLSConfig**: Configuration management

## 🔧 Areas for Contribution

We welcome contributions in these areas:

### High Priority
- **DASH support**: Add Dynamic Adaptive Streaming over HTTP
- **Cloud storage integration**: S3, Google Cloud Storage, Azure
- **Improved error handling**: Better error messages and recovery
- **Performance optimization**: Reduce memory usage and processing time

### Medium Priority
- **Additional encoder support**: AV1, HEVC, VP9
- **Advanced filtering**: Deinterlacing, noise reduction, scaling algorithms
- **Metadata preservation**: Chapters, tags, custom metadata
- **Progress callback system**: For GUI integration

### Low Priority
- **GUI application**: Desktop application with drag-and-drop
- **Docker containerization**: Official Docker images
- **Plugin system**: Allow custom processors and filters
- **Benchmarking tools**: Performance testing utilities

## 🧪 Testing Guidelines

### Test Categories

1. **Unit Tests**: Test individual components
2. **Integration Tests**: Test component interactions
3. **End-to-End Tests**: Test complete workflows
4. **Performance Tests**: Test processing speed and memory usage

### Test Data

- Use small test videos (< 10MB) for automated testing
- Include various formats: MP4, MKV, AVI, MOV
- Test edge cases: very short videos, audio-only, subtitle-only

### Mock External Dependencies

Mock FFmpeg calls for unit tests to ensure fast, reliable testing:

```python
from unittest.mock import patch, MagicMock

@patch('subprocess.run')
def test_encoder_detection(mock_run):
    mock_run.return_value = MagicMock(returncode=0, stdout='test output')
    # Test encoder detection logic
```

## 📖 Documentation Standards

### Code Documentation
- Use Google-style docstrings
- Document all public APIs
- Include examples in docstrings
- Keep docstrings up-to-date with code changes

### README Updates
- Update feature lists for new functionality
- Add usage examples for new CLI options
- Update API documentation for new classes/methods
- Keep installation instructions current

## ❓ Getting Help

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Code Review**: We provide thorough code review feedback

## 🎉 Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes for significant contributions
- GitHub contributors page

Thank you for contributing to HLS Converter! 🙏