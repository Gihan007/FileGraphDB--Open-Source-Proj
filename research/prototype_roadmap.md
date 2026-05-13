# FileGraphDB Prototype Roadmap

## Goal

Build a minimal file-native graph database over an ordinary folder.

The first version should prove this:

> A normal project directory can be scanned into a typed relationship graph, queried locally, and used to answer questions that are hard for folder navigation or vector search alone.

## MVP Scope

Do not replace the filesystem.

Use:

- Python
- SQLite
- Plain files
- Deterministic extractors first
- Optional LLM extraction later

## Milestone 1: Filesystem Graph

Create nodes:

- `Directory`
- `File`

Create edges:

- `CONTAINS`

Store properties:

- path
- extension
- size
- modified time
- content hash

Success test:

```powershell
python -m filegraph scan .
python -m filegraph query files
python -m filegraph query related small_llm.py
```

## Milestone 2: Static Relationship Extraction

Add extractors:

- Markdown links: `[[note]]`, `[text](file.md)`
- Python imports: `import x`, `from x import y`
- Local path references: strings that look like filenames

Create edges:

- `LINKS_TO`
- `IMPORTS`
- `REFERENCES`

Success test:

```powershell
python -m filegraph scan .
python -m filegraph query depends-on small_llm.py
python -m filegraph query why small_llm.py requirements.txt
```

## Milestone 3: Explainability

Every edge needs evidence.

Example:

```json
{
  "source": "small_llm.py",
  "target": "requirements.txt",
  "type": "REFERENCES",
  "evidence": "README.md mentions pip install -r requirements.txt",
  "extractor": "markdown-link-extractor",
  "confidence": 1.0
}
```

Commands:

```powershell
python -m filegraph query why README.md requirements.txt
python -m filegraph query edges --type REFERENCES
```

## Milestone 4: Research Queries

Support practical questions:

```text
What files depend on this file?
What files are probably related to this file?
What files have no relationships?
What generated this artifact?
What data does this script use?
What notes mention this concept?
```

CLI commands:

```powershell
python -m filegraph query used-by path/to/file
python -m filegraph query orphans
python -m filegraph query path file_a file_b
```

## Milestone 5: AI-Assisted Edges

Use a small local LLM only after deterministic extraction works.

AI edge rules:

- Store as `suggested=true`.
- Store confidence below `1.0`.
- Store evidence spans.
- Let user accept or reject.

Possible edge types:

- `SUMMARIZES`
- `IMPLEMENTS`
- `MENTIONS_CONCEPT`
- `SEMANTICALLY_RELATED_TO`
- `CONTRADICTS`

## Milestone 6: Evaluation

Create a small test corpus:

```text
sample_workspace/
  notes/
  papers/
  data/
  scripts/
  outputs/
  reports/
```

Create questions with known answers:

```text
Which script generated this chart?
Which dataset supports this report?
Which notes are related to this idea but not directly linked?
Which file explains this function?
Which files would be affected if this dataset changes?
```

Compare:

- keyword search
- vector search
- graph traversal
- graph + vector hybrid

## First Implementation Order

1. SQLite schema.
2. Directory scanner.
3. File hashing.
4. `CONTAINS` edges.
5. Markdown extractor.
6. Python import extractor.
7. CLI commands.
8. Evidence display.
9. Sample workspace.
10. Optional LLM relation extraction.

## Research Output

The final research artifact can include:

- Literature review.
- Prototype implementation.
- Relationship schema.
- Query examples.
- Evaluation against baseline search.
- Discussion of limits and failure cases.

Possible title:

> FileGraphDB: A Local-First Graph Layer for Relationship-Aware File Systems
