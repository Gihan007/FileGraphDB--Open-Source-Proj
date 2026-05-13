# FileGraphDB Open-Source Launch Checklist

Use this checklist after creating the GitHub repository.

## Repository Settings

- Repository name: `FileGraphDB--Open-Source-Proj`
- Description: `A local file-native graph layer for relationship-aware text retrieval.`
- Visibility: Public
- License: MIT
- Python package: `filegraphdb`
- CLI command: `filegraph`

## Values To Replace

Replace these placeholders before publishing:

- Confirm the repository URL in `pyproject.toml`
- Confirm the clone URL in `CONTRIBUTING.md`
- Copyright holder in `LICENSE` if you want your personal name instead of
  `FileGraphDB contributors`

## Suggested GitHub Labels

- `good first issue`
- `help wanted`
- `documentation`
- `bug`
- `enhancement`
- `question`

## First Beginner-Friendly Issues

1. Improve README quick-start example.
2. Add more examples to `examples/basic_usage.py`.
3. Add tests for graph relationships and retrieval ranking.
4. Add docstrings to public methods in `filegraphdb/core.py`.
5. Improve installation instructions for Windows users.

Suggested labels: `good first issue`, `help wanted`, `documentation`.

Use `ROADMAP.md` to create more contributor-friendly issues for intermediate
and advanced work.

## Announcement Draft

I created an open-source Python library called FileGraphDB.

It helps turn a local folder of text files into a relationship graph for LLM and
RAG workflows, so related documents and chunks can be retrieved together.

I am looking for contributors who can help with documentation, examples, tests,
and new features. Beginner-friendly issues are available with the
`good first issue` label.

GitHub repo: https://github.com/Gihan007/FileGraphDB--Open-Source-Proj

Feedback is welcome.

## Reply Templates

When someone asks to work on an issue:

```text
Yes, thank you! You can work on this issue. Please create a fork, make the
changes, and open a pull request. Let me know if you need help setting up the
project.
```

When someone opens a pull request:

```text
Thank you for the contribution! I will review it and give feedback.
```
