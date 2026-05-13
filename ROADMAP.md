# Roadmap

This roadmap lists contribution ideas for FileGraphDB. If you want to work on
one, open or comment on a GitHub issue first so the scope can stay clear.

## Good First Contributions

These are small tasks for new contributors.

### Improve Quick Start Examples

Add one or two short examples that show common FileGraphDB workflows.

Suggested files:

- `README.md`
- `examples/basic_usage.py`

Acceptance criteria:

- Example can be copied and run locally.
- Existing tests pass with `python -m pytest`.

### Add Public Method Docstrings

Add short docstrings to the main `FileGraphDB` methods.

Suggested files:

- `filegraphdb/core.py`

Methods to document:

- `build()`
- `retrieve()`
- `related()`
- `context_for_query()`
- `estimate_token_savings()`

Acceptance criteria:

- Docstrings explain arguments and return values briefly.
- Existing tests pass with `python -m pytest`.

### Improve Windows Installation Notes

Make setup instructions clearer for Windows users.

Suggested files:

- `README.md`
- `CONTRIBUTING.md`

Acceptance criteria:

- Instructions include virtual environment activation.
- Instructions include editable install and test command.

## Intermediate Contributions

These tasks are useful next steps for the project.

### Add More Document Loaders

FileGraphDB currently works best with text-like files. Add optional loaders for
common document types.

Possible formats:

- PDF
- DOCX
- HTML
- Jupyter notebooks
- source code files with language-aware metadata

Suggested approach:

- Keep new dependencies optional when possible.
- Add tests using tiny fixture files.
- Document any optional install extras.

Acceptance criteria:

- Loader skips unsupported or unreadable files gracefully.
- Tests cover at least one successful load path.
- README includes a short usage note.

### Add Persistent Embedding Cache

Avoid rebuilding embeddings for unchanged files.

Suggested design:

- Cache by file content hash.
- Include embedding model name in the cache key.
- Reuse cached embeddings when file content has not changed.
- Rebuild only changed documents.

Acceptance criteria:

- Cache behavior is tested.
- Changing a file invalidates only that file's cached embedding.
- Existing retrieval behavior remains compatible.

### Improve Retrieval Ranking

Make graph-aware retrieval more useful for relationship questions.

Possible improvements:

- BM25 keyword scoring
- graph centrality scoring
- query expansion
- multi-hop traversal controls
- source diversity ranking
- optional reranking step

Acceptance criteria:

- Add tests or evaluation cases showing the ranking improvement.
- Keep default behavior stable unless the change is clearly better.
- Document any new options.

## Advanced Contributions

These are larger project directions. They should start with a design issue
before implementation.

### Add Vector Index Support

Add optional fast vector search for larger folders.

Possible backends:

- FAISS
- HNSWLib
- Annoy
- SQLite vector extensions

Acceptance criteria:

- Backend is optional.
- Small projects still work without extra dependencies.
- Tests cover fallback behavior when the backend is not installed.

### Build A Local Web UI

Create a local browser interface for exploring files, graph edges, and search
results.

Possible features:

- select or configure a folder
- build graph
- search queries
- view related files
- preview file contents
- inspect graph nodes and edges
- export LLM-ready context

Acceptance criteria:

- UI can run locally from the repository.
- README documents how to start it.
- Core package remains usable without the UI.

### Add More Graph Relationship Types

Make relationships more expressive than simple similarity.

Possible edge types:

- `SUPPORTS`
- `CONTRADICTS`
- `MENTIONS_ENTITY`
- `CITES`
- `DUPLICATES`
- `SAME_PROJECT`

Acceptance criteria:

- New edge types include evidence strings.
- Tests cover edge creation.
- Documentation explains when each edge type is used.

### Add Evaluation Benchmarks

Build stronger benchmark reports comparing FileGraphDB with plain RAG.

Metrics to track:

- hit@k
- mean reciprocal rank
- file recall
- answer-term recall
- token savings
- runtime
- memory usage

Acceptance criteria:

- Benchmark command is documented.
- Results are reproducible from sample data.
- Report output is easy to read.

### Add GitHub Actions

Run automated checks on every pull request.

Suggested workflow:

- install Python
- install package with dev dependencies
- run `python -m pytest`
- optionally check package build

Acceptance criteria:

- Pull requests show test status.
- Workflow uses supported Python versions.
- README badge can be added after the workflow is passing.

### Prepare PyPI Release Automation

Make package releases easier and safer.

Possible tasks:

- add release checklist
- add changelog
- build source and wheel artifacts
- publish with trusted publishing
- create GitHub releases

Acceptance criteria:

- Release process is documented.
- Package build is tested before publishing.
- Version updates are clear.

## How To Pick A Task

1. Choose a task from this roadmap.
2. Open a GitHub issue or comment on an existing one.
3. Keep the first pull request small.
4. Add tests or documentation when behavior changes.

Beginner-friendly tasks should use the `good first issue` label. Larger tasks
should usually use `help wanted` or `enhancement`.
