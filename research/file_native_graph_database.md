# File-Native Graph Database Research Brief

## 1. Short Answer

The idea is not completely new, but there is still a strong research gap.

Many systems already connect files, documents, or data objects as graphs. Examples include semantic file systems, note-linking tools, graph databases, content-addressed storage systems, and code dependency analyzers.

The more defensible research claim is:

> There is no widely adopted, general-purpose, file-native graph database layer that treats ordinary files as first-class graph nodes and supports typed relationships, semantic relationships, provenance, querying, versioning, and normal filesystem compatibility.

That is the useful gap.

## 2. What Already Exists

### 2.1 Traditional File Systems

Most filesystems expose files through a directory tree:

```text
folder -> subfolder -> file
```

This is already a graph in a narrow technical sense, because directories point to files and symlinks can create non-tree edges. But the exposed user model is mostly hierarchical.

Limitations:

- Relationships are mostly `contains`.
- Cross-file meaning is usually hidden inside file content.
- Querying relationships requires external tools.
- Semantic edges such as `derived_from`, `cites`, `implements`, `uses_dataset`, or `contradicts` are not first-class.

### 2.2 Semantic File Systems

The classic Semantic File System work from MIT proposed extracting attributes from files using file-type-specific transducers, then exposing query results as virtual directories.

Important idea:

- Files remain compatible with ordinary filesystem access.
- Metadata is automatically extracted from content.
- Users can navigate by meaning, not only by location.

Source:

- Semantic File Systems, Gifford, Jouvelot, Sheldon, O'Toole: https://www.researchgate.net/publication/2503061_Semantic_File_Systems

Why this matters:

This is a direct ancestor. It shows that "semantic access to files" is old and serious. A new project must explain what is different today: graph relationships, LLM extraction, embeddings, provenance, project-scale workflows, and developer-friendly local databases.

### 2.3 WinFS

Microsoft WinFS attempted to combine files, metadata, structured objects, relationships, and synchronization. It was not simply a normal filesystem; it sat over NTFS and used a richer storage model.

Source:

- Microsoft Research, Peer-to-Peer Replication in WinFS: https://www.microsoft.com/en-us/research/publication/peer-to-peer-replication-in-winfs/

Why this matters:

WinFS is a major prior-art warning. A file graph system must avoid requiring the operating system to replace the user's existing filesystem. A practical modern version should work as an overlay or sidecar index.

### 2.4 Quasar File System / QFS

QFS is very close to the research idea. Its abstract describes a metadata-rich filesystem where files, metadata, and file relationships are first-class objects, with a graph data model over files and relationships.

Source:

- UCSC technical report on QFS: https://tr.soe.ucsc.edu/research/technical-reports/UCSC-SOE-09-32

Why this matters:

This means the exact phrase "graph data model composed of files and relationships" already exists in prior work. The novelty should not claim first invention. The novelty should claim a modern, usable, general, local-first graph layer with AI-assisted relation extraction and ordinary file compatibility.

### 2.5 Copernicus

Copernicus proposed a scalable semantic filesystem for billions of files. It used a dynamic graph-based filesystem design to index attributes and relationships.

Source:

- Copernicus: A Scalable, High-Performance Semantic File System: https://crss.us/pub/leung-ssrctr09-06.html

Why this matters:

This is another close ancestor. It focuses on scale and search/navigation of files. A new project should differentiate through use cases like research workspaces, code/data provenance, GraphRAG, reproducibility, and human-editable relationship layers.

### 2.6 Obsidian and Note Graphs

Obsidian connects Markdown notes through internal links and visualizes them as nodes and edges.

Source:

- Obsidian Graph View docs: https://obsidian.md/help/Plugins/Graph%2Bview

Why this matters:

Obsidian proves users like file-level graph navigation. But it is mainly note-centric. Relationships are usually links, backlinks, tags, and attachments. It does not provide a general typed graph database over arbitrary project files.

### 2.7 Graph Databases

Graph databases such as Neo4j, JanusGraph, RDF triple stores, and TerminusDB can model files as nodes and relationships as edges.

TerminusDB is especially relevant because it is a document graph database with versioning, schema, diff, branch, and merge.

Source:

- TerminusDB explanation: https://terminusdb.org/docs/terminusdb-explanation/

Why this matters:

Existing graph DBs can store file metadata, but they usually do not treat the normal filesystem as the primary user-facing database. The files often become imported records, not living first-class filesystem objects.

### 2.8 IPLD and Content-Addressed Graphs

IPLD models content-addressed data with bytes, structured data, and links. It supports traversal across hash-linked data.

Source:

- IPLD Data Model: https://ipld.io/docs/data-model/

Why this matters:

IPLD shows that data objects can form traversable graphs independent of a single storage format. It is powerful prior art for content-addressed links, but it is not the same as a user-facing file relationship database for ordinary local folders.

## 3. The Gap

The gap is not "nobody connects files."

The gap is:

- Ordinary folders are still the default working surface.
- File relationships are scattered across imports, citations, comments, filenames, metadata, generated artifacts, hidden caches, Git history, and human memory.
- Existing tools usually specialize in one relationship type: Markdown links, code imports, data lineage, citations, or filesystem metadata.
- Graph databases can store the graph, but they are not usually file-native.
- Semantic filesystems existed, but they did not become a mainstream developer or researcher workflow.
- Modern AI systems need graph-aware file context, but most local RAG tools flatten files into chunks and embeddings.

## 4. Proposed Research Direction

Working name:

> FileGraphDB

Definition:

> A file-native graph database is a sidecar database for a normal directory tree where files, directories, chunks, symbols, metadata, versions, and generated artifacts are first-class nodes connected by typed, queryable, explainable relationships.

Core principle:

> The filesystem remains the source of truth for bytes. The graph database becomes the source of truth for relationships.

## 5. Node Types

Minimal node model:

```text
File
Directory
Chunk
Symbol
Person
Dataset
Model
Run
Artifact
Commit
Concept
ExternalResource
```

Examples:

```text
File(path="paper.pdf")
File(path="analysis.py")
Dataset(path="data/results.csv")
Chunk(file="notes.md", start=120, end=245)
Symbol(file="small_llm.py", name="SmallLLM", kind="class")
```

## 6. Edge Types

Useful relationships:

```text
CONTAINS
IMPORTS
REFERENCES
CITES
MENTIONS
DEFINES
CALLS
GENERATED_BY
DERIVED_FROM
USES_DATASET
PRODUCES
DEPENDS_ON
SIMILAR_TO
CONTRADICTS
SUMMARIZES
IMPLEMENTS
CONFIGURES
DOCUMENTS
VERSION_OF
RENAMED_FROM
```

Each edge should have:

```text
source_node
target_node
type
confidence
evidence
extractor
created_at
updated_at
```

The `evidence` field matters. A graph edge should be explainable:

```text
analysis.py --USES_DATASET--> results.csv
evidence: "line 17: pd.read_csv('data/results.csv')"
extractor: "python-static-parser"
confidence: 1.0
```

## 7. Why LLMs Matter Now

Older semantic filesystems relied on deterministic transducers. That remains important for code, metadata, citations, and structured formats.

Modern systems can add:

- Semantic extraction from messy prose.
- Relationship suggestions.
- Natural-language graph queries.
- Entity resolution across files.
- GraphRAG over files, chunks, and typed edges.

But LLM output should not be blindly trusted. LLM-generated edges should be marked with lower confidence unless grounded in evidence.

Example:

```text
design.md --IMPLEMENTS_IDEA_FROM--> paper.pdf
evidence: "LLM explanation with quoted spans from both files"
extractor: "llm-relation-extractor"
confidence: 0.68
```

## 8. Research Questions

Good research questions:

1. Can file-level graph modeling improve retrieval quality compared to chunk-only vector search?
2. Can typed relationships reduce hallucination in local AI assistants?
3. What edge types are most useful for research projects, codebases, and data science workflows?
4. How should a file graph handle file moves, renames, copies, and edits?
5. Should identity be path-based, content-hash-based, inode-based, Git-object-based, or hybrid?
6. Can users understand and correct automatically inferred relationships?
7. What query language is natural for file relationships?
8. Can this work as a sidecar without replacing the filesystem?

## 9. Possible Architecture

```text
normal project folder
        |
        v
file watcher / scanner
        |
        v
extractors
  - filesystem metadata
  - Markdown links
  - code imports
  - PDF citations
  - CSV/data lineage
  - image/audio metadata
  - LLM relation extraction
        |
        v
graph store
  - SQLite tables
  - DuckDB
  - Neo4j
  - TerminusDB
  - RDF store
        |
        v
query layer
  - CLI
  - Python API
  - natural language query
  - visualization
```

For this project, start simple:

```text
files on disk + SQLite graph sidecar + Python extractors
```

## 10. Minimal Prototype

MVP goal:

> Scan a folder, create graph nodes for files, extract relationships, and answer simple graph queries.

Phase 1:

- Scan all files in a directory.
- Create `File` nodes.
- Create `Directory CONTAINS File` edges.
- Hash file contents.
- Track modified time and size.

Phase 2:

- Extract Markdown links.
- Extract Python imports.
- Extract local file path references.
- Store typed edges in SQLite.

Phase 3:

- Add CLI queries:
  - `related path/to/file`
  - `depends-on path/to/file`
  - `used-by path/to/file`
  - `orphans`
  - `why file_a file_b`

Phase 4:

- Add semantic edges with embeddings or a small LLM.
- Mark AI edges as suggested until confirmed.

## 11. Evaluation Ideas

Compare these retrieval approaches:

1. Keyword search only.
2. Vector search over chunks.
3. File graph traversal only.
4. Hybrid graph + vector retrieval.

Possible metrics:

- Retrieval precision.
- Retrieval recall.
- Multi-hop question accuracy.
- User time to find relevant files.
- Explainability of retrieved context.
- Robustness after file rename/move.

Example task:

```text
Question: Which scripts generated the chart used in report.md?
```

A graph-aware system can traverse:

```text
report.md --EMBEDS--> chart.png
chart.png --GENERATED_BY--> plot_results.py
plot_results.py --USES_DATASET--> results.csv
```

Vector search alone may miss the chain.

## 12. Novelty Claim Draft

A careful claim:

> This project revisits semantic file systems in the context of modern AI-assisted research and development workflows. Instead of replacing the filesystem, it introduces a sidecar file-native graph layer that models files, chunks, symbols, generated artifacts, provenance, semantic relationships, and user-confirmed links as a typed, queryable, explainable graph over ordinary directories.

What not to claim:

> "No one has ever represented files as graphs."

That is false.

Better claim:

> "Existing systems either focus on metadata search, note links, specialized dependency graphs, content-addressed object graphs, or standalone graph databases. There remains a practical gap for a general, local-first, file-native graph database that works directly over ordinary project folders and integrates deterministic extraction with AI-assisted relationship discovery."

## 13. Next Build Step

Build a small Python package:

```text
filegraph/
  scanner.py
  store.py
  extractors/
    markdown.py
    python_imports.py
    path_refs.py
  cli.py
```

SQLite schema:

```sql
CREATE TABLE nodes (
  id TEXT PRIMARY KEY,
  type TEXT NOT NULL,
  path TEXT,
  content_hash TEXT,
  properties_json TEXT NOT NULL
);

CREATE TABLE edges (
  id TEXT PRIMARY KEY,
  source_id TEXT NOT NULL,
  target_id TEXT NOT NULL,
  type TEXT NOT NULL,
  confidence REAL NOT NULL,
  evidence TEXT,
  extractor TEXT NOT NULL,
  properties_json TEXT NOT NULL
);
```

This is enough to start doing actual experiments.

## 14. Source List

- Semantic File Systems: https://www.researchgate.net/publication/2503061_Semantic_File_Systems
- WinFS replication paper: https://www.microsoft.com/en-us/research/publication/peer-to-peer-replication-in-winfs/
- Quasar File System / QFS: https://tr.soe.ucsc.edu/research/technical-reports/UCSC-SOE-09-32
- Copernicus semantic file system: https://crss.us/pub/leung-ssrctr09-06.html
- Obsidian Graph View: https://obsidian.md/help/Plugins/Graph%2Bview
- TerminusDB explanation: https://terminusdb.org/docs/terminusdb-explanation/
- IPLD Data Model: https://ipld.io/docs/data-model/
