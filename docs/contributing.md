# Contributing

Thanks for your interest in contributing! This guide explains how to set up your environment, run tests, and submit changes.

## Development Setup

- Python 3.13 (or 3.8+)
- FFmpeg installed and available in PATH
- Create and activate a virtual environment, then install dev deps:

```bash
pip install -r requirements.txt
pip install -r requirements-docs.txt
```

## Running Tests

```bash
pytest -q
```

## Docs

```bash
mkdocs serve
```

## Commit Guidelines

- Keep commits focused and well-described.
- Include tests where behavior changes.
- Update docs for user-facing changes.

## Code Style

- Follow PEP8 and use Black/ruff (if configured).

## Reporting Issues

Please include:
- OS, Python version, FFmpeg version
- Steps to reproduce
- Expected vs actual behavior
