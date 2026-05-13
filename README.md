# FileGraphDB

FileGraphDB is a local Python library that turns a folder of files into a relationship graph for LLM and RAG workflows.

Instead of treating a folder as only isolated chunks, FileGraphDB builds:

```text
File nodes
Chunk nodes
File-to-file edges
Chunk-to-chunk edges
File CONTAINS Chunk edges
```

The goal is to help an LLM retrieve useful context without reading every file in the folder.

## Install

```powershell
pip install -U filegraphdb
```

Optional open-source embedding model support:

```powershell
pip install -U "filegraphdb[models]"
```

For local development from this repo:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
```

For contributors who want to run tests:

```powershell
pip install -e ".[dev]"
pytest
```

## Project Status

FileGraphDB is in early development. The core package can scan local text files,
build relationship edges, run graph-aware retrieval, estimate token savings, and
create interactive graph visualizations. Contributors are welcome.

## Quick Start

Create a small demo folder:

```powershell
mkdir demo_docs
Set-Content demo_docs\project_timeline.txt "The product launch was delayed because the vendor shipment arrived late. The engineering team moved the beta release to Friday."
Set-Content demo_docs\vendor_delay.txt "The vendor reported a shipment delay for the beta hardware. This delay affected the launch timeline."
Set-Content demo_docs\budget_notes.txt "The budget review approved extra spending for testing, support, and deployment."
Set-Content demo_docs\garden_plan.txt "The garden plan includes tomatoes, basil, and irrigation setup for the weekend."
```

Build and search with Python:

```python
from filegraphdb import FileGraphDB

graph = FileGraphDB("./demo_docs")
summary = graph.build()

print(summary)

results = graph.retrieve("what caused the launch delay?", limit=3)

for result in results:
    print(result.document.rel_path, round(result.score, 3), result.reason)
```

Build and search with CLI:

```powershell
filegraph --folder ./demo_docs build
filegraph --folder ./demo_docs search "what caused the launch delay?" --limit 3
```

## What Gets Built

Files longer than `2,000` words keep their file node and are also split into overlapping chunk nodes:

```text
big_report.txt
big_report.txt#chunk-0001
big_report.txt#chunk-0002
```

Relationship types:

```text
File --CONTAINS--> Chunk
File --REFERENCES--> File
File --SEMANTICALLY_SIMILAR--> File
Chunk --SEMANTICALLY_SIMILAR--> Chunk
File/Chunk --SHARES_ENTITY--> File/Chunk
File/Chunk --SHARES_TOPIC--> File/Chunk
```

The local graph is stored in SQLite:

```text
.filegraphdb.sqlite
```

## Python Examples

Retrieve relevant files or chunks:

```python
from filegraphdb import FileGraphDB

graph = FileGraphDB("./demo_docs")
graph.build()

results = graph.retrieve("what caused the launch delay?", limit=3)

for result in results:
    print(result.document.rel_path, round(result.score, 3), result.reason)
```

Generate LLM-ready context:

```python
from filegraphdb import FileGraphDB

graph = FileGraphDB("./demo_docs")
graph.build()

context = graph.context_for_query("what caused the launch delay?", limit=2)

print(context)
```

Inspect graph edges:

```python
from filegraphdb import FileGraphDB

graph = FileGraphDB("./demo_docs")
graph.build()

for edge in graph.edges(limit=10):
    print(edge.source_path, edge.type, edge.target_path, edge.weight)
    print(edge.evidence)
```

Find files related to one file:

```python
from filegraphdb import FileGraphDB

graph = FileGraphDB("./demo_docs")
graph.build()

for edge in graph.related("project_timeline.txt", limit=5):
    print(edge.source_path, edge.type, edge.target_path, edge.weight)
    print(edge.evidence)
```

Estimate token savings:

```python
from filegraphdb import FileGraphDB

graph = FileGraphDB("./demo_docs")
graph.build()

estimate = graph.estimate_token_savings(
    "what caused the launch delay?",
    limit=2,
    price_per_million_input_tokens=0.15,
)

print(estimate)
```

Tune relationship building:

```python
from filegraphdb import FileGraphDB

graph = FileGraphDB(
    "./demo_docs",
    min_relationship_score=0.2,
    max_edges_per_file=10,
)

summary = graph.build()

print(summary)
```

Tune chunking:

```python
from filegraphdb import FileGraphDB

graph = FileGraphDB(
    "./demo_docs",
    chunk_word_threshold=2000,
    chunk_words=800,
    chunk_overlap=120,
)

summary = graph.build()

print(summary)
```

Use an open-source embedding model:

```python
from filegraphdb import FileGraphDB

graph = FileGraphDB(
    "./demo_docs",
    use_sentence_transformers=True,
    embedding_model="all-MiniLM-L6-v2",
)

graph.build()

results = graph.retrieve("vendor shipment affected release timeline", limit=3)

for result in results:
    print(result.document.rel_path, round(result.score, 3))
```

## CLI Examples

Build:

```powershell
filegraph --folder ./demo_docs build
```

Search:

```powershell
filegraph --folder ./demo_docs search "what caused the launch delay?" --limit 3
```

Print LLM-ready context:

```powershell
filegraph --folder ./demo_docs context "what caused the launch delay?" --limit 2
```

Show strongest graph edges:

```powershell
filegraph --folder ./demo_docs edges --limit 10
```

Find related files:

```powershell
filegraph --folder ./demo_docs related project_timeline.txt --limit 5
```

Estimate token savings:

```powershell
filegraph --folder ./demo_docs estimate "what caused the launch delay?" --limit 2 --price-per-million 0.15
```

Tune relationship edges:

```powershell
filegraph --folder ./demo_docs build --min-score 0.2 --max-edges 10
```

Tune chunking:

```powershell
filegraph --folder ./demo_docs --chunk-threshold 2000 --chunk-words 800 --chunk-overlap 120 build
```

Disable chunking:

```powershell
filegraph --folder ./demo_docs --chunk-threshold 0 build
```

Use sentence-transformers if installed:

```powershell
filegraph --folder ./demo_docs --use-model build
```

## Visualization

Create an interactive HTML graph:

```powershell
filegraph --folder ./demo_docs build
filegraph --folder ./demo_docs visualize --out demo_graph.html
```

Python visualization:

```python
from filegraphdb import FileGraphDB
from filegraphdb.visualize import visualize_graph

graph = FileGraphDB("./demo_docs")
graph.build()

result = visualize_graph(
    folder="./demo_docs",
    out_path="demo_graph.html",
    limit_edges=100,
    min_weight=0.0,
)

print(result)
```

The visualization shows file bubbles, chunk bubbles, and relationship edges.

## Evaluation

Create a small evaluation file:

```powershell
@'
{"query":"what caused the launch delay?","expected_files":["vendor_delay.txt","project_timeline.txt"],"expected_terms":["vendor","shipment","delay","launch"]}
{"query":"what document talks about garden planning?","expected_files":["garden_plan.txt"],"expected_terms":["garden","tomatoes","irrigation"]}
'@ | Set-Content demo_eval.jsonl
```

Run evaluation:

```powershell
filegraph --folder ./demo_docs eval demo_eval.jsonl --limit 3 --show-cases
```

Metrics include:

```text
hit@k
MRR
file recall
answer-term recall
token savings estimate
```

## Relationship Demo

This example shows where FileGraphDB becomes more useful than plain top-k chunk search.

Create relationship-focused files:

```powershell
mkdir relationship_demo
Set-Content relationship_demo\53294.txt "The writer argues that handgun restrictions reduce public safety because lawful citizens lose the ability to defend themselves. The message discusses waiting periods, defensive gun use, and crime deterrence."
Set-Content relationship_demo\53318.txt "This document supports the same argument as 53294. It says that gun control laws mostly affect lawful owners, while criminals ignore restrictions. It also mentions defensive gun use and deterrence."
Set-Content relationship_demo\53372.txt "The author discusses handgun bans, self defense, and crime deterrence. The document argues that armed citizens can prevent crime and that restrictions may punish responsible owners."
Set-Content relationship_demo\54000.txt "This document argues the opposite view. It says handgun restrictions and waiting periods may reduce violence and accidental shootings."
Set-Content relationship_demo\budget.txt "The team budget includes cloud hosting, software licenses, and customer support allocation."
Set-Content relationship_demo\garden.txt "The garden plan includes basil, tomatoes, irrigation, compost, and weekend planting."
```

Build and inspect related files:

```python
from filegraphdb import FileGraphDB

graph = FileGraphDB(
    "./relationship_demo",
    min_relationship_score=0.2,
    max_edges_per_file=10,
)

summary = graph.build()
print(summary)

for edge in graph.related("53294.txt", limit=10):
    print(edge.source_path, edge.type, edge.target_path, edge.weight)
    print(edge.evidence)
```

Ask relationship-style queries:

```python
from filegraphdb import FileGraphDB

graph = FileGraphDB("./relationship_demo", min_relationship_score=0.2, max_edges_per_file=10)
graph.build()

queries = [
    "what does file 53294 argue?",
    "which documents support the same argument as file 53294?",
    "find files connected to 53294 through self defense, handgun restrictions, or deterrence",
    "which documents discuss the opposite side of the handgun restriction argument?",
    "show me the document cluster around handgun laws and public safety",
]

for query in queries:
    print()
    print("QUERY:", query)
    for result in graph.retrieve(query, limit=4, graph_hops=1):
        print(result.document.rel_path, round(result.score, 3), result.reason, result.via)
```

Generate a relationship graph visualization:

```powershell
filegraph --folder ./relationship_demo build --min-score 0.2 --max-edges 10
filegraph --folder ./relationship_demo visualize --out relationship_demo_graph.html --limit-edges 100 --min-weight 0.0
```

## When FileGraphDB Helps

Normal RAG is strong for direct questions:

```text
What is the answer to this question?
Which chunk contains this fact?
Summarize the most relevant passages.
Find documents matching these keywords.
Retrieve top chunks by embedding similarity.
```

FileGraphDB is useful when the question is about relationships:

```text
Which documents support the same argument as file X?
Which documents disagree with file X but discuss the same topic?
Which files are related to this file through shared entities?
Which files are related to this file through shared topics?
Which chunks belong to this large file?
Which chunks from different files discuss the same idea?
Which files should be read together before answering?
Which documents form the evidence cluster for this claim?
Which files mention the same person, company, law, event, or product?
Which documents reference this file by name?
Which files are semantically similar but do not share exact keywords?
Which files contain duplicate or near-duplicate arguments?
Which documents connect topic A to topic B?
Which files explain the background around this document?
Which related files can reduce LLM context size for this question?
```

## How It Works

Current retrieval signals:

```text
TF-IDF keyword similarity
LSA semantic similarity using TruncatedSVD
Optional sentence-transformers embeddings
Cosine similarity
Entity overlap
Topic overlap
Direct filename/path reference detection
Graph expansion through related nodes
```

Current relationship score:

```text
0.46 * semantic_score
+ 0.24 * keyword_score
+ 0.14 * entity_overlap
+ 0.10 * topic_overlap
+ 0.06 * direct_reference
```

## More Examples

More copy-paste examples are available in:

```text
reports/filegraphdb_code_only_examples.md
reports/filegraphdb_code_only_examples.pdf
```

## Roadmap

Planned improvements:

```text
PDF, DOCX, Markdown loaders
Persistent embedding cache
FAISS/HNSW vector index support
Better entity extraction
LLM-based relationship labels
Better graph ranking
More evaluation benchmarks
More scalable graph construction for very large folders
```

See `ROADMAP.md` for contributor-friendly task ideas, acceptance criteria, and
larger development directions.

## Contributing

We welcome contributions. Good first tasks include improving documentation,
adding examples, expanding tests, fixing bugs, and suggesting focused features.

See `CONTRIBUTING.md` for setup instructions and pull request guidelines. See
`ROADMAP.md` for tasks you can pick up.

## License

FileGraphDB is licensed under the MIT License. See `LICENSE` for details.

## Small LLM Demo

The earlier local LLM demo is still available:

```powershell
python small_llm.py
```
