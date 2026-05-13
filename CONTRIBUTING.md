# Contributing Guide

Thank you for your interest in contributing to FileGraphDB.

FileGraphDB is an early-stage Python library for building relationship-aware
graphs from local files. Documentation, tests, examples, bug fixes, and small
feature improvements are all welcome.

## Set Up The Project

```bash
git clone https://github.com/Gihan007/FileGraphDB--Open-Source-Proj.git
cd FileGraphDB--Open-Source-Proj

python -m venv .venv
```

Activate the environment on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

Activate the environment on macOS or Linux:

```bash
source .venv/bin/activate
```

Install the package locally with test tools:

```bash
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

## How To Contribute

1. Pick an issue.
2. Comment that you want to work on it.
3. Fork the repository.
4. Create a branch for your change.
5. Make your changes.
6. Run tests.
7. Open a pull request.

## Pull Request Guidelines

Keep changes small and focused. Add tests when you change behavior, update the
README or examples when user-facing behavior changes, and explain what problem
your pull request solves.

Good first contribution ideas:

- Improve README examples.
- Add more files to `examples/`.
- Add tests for `FileGraphDB.retrieve()`.
- Add docstrings to public methods.
- Improve Windows setup notes.

## Development Notes

Generated graph databases named `.filegraphdb.sqlite` should not be committed.
Build output such as `dist/`, `build/`, and `*.egg-info/` is ignored by Git.

## Community

Please be kind, patient, and constructive. This project follows the expectations
in `CODE_OF_CONDUCT.md`.
