# FileGraphDB Codebase Graph

This file is a visual map of how the current codebase connects.

## 1. Module Dependency Graph

```mermaid
flowchart TD
    User[User / Terminal / Python Script]
    CLI[filegraphdb/cli.py<br/>CLI commands]
    Init[filegraphdb/__init__.py<br/>public imports]
    Core[filegraphdb/core.py<br/>FileGraphDB main API]
    Scanner[filegraphdb/scanner.py<br/>folder scan + text cleanup]
    Features[filegraphdb/text_features.py<br/>TF-IDF, LSA, entities, topics]
    Store[filegraphdb/store.py<br/>SQLite nodes + edges]
    Models[filegraphdb/models.py<br/>Document, Edge, SearchResult]
    Eval[filegraphdb/eval.py<br/>retrieval evaluation]
    Report[scripts/eval_report.py<br/>markdown eval report]
    Test[test_main.py<br/>small usage test]
    LLM[small_llm.py<br/>separate local LLM demo]

    User --> CLI
    User --> Test
    User --> Report

    Test --> Init
    Init --> Core
    Init --> Models

    CLI --> Core
    CLI --> Eval

    Report --> Init
    Report --> Eval

    Eval --> Core

    Core --> Scanner
    Core --> Features
    Core --> Store
    Core --> Models

    Scanner --> Models
    Features --> Models
    Store --> Models

    LLM -. separate demo .-> User
```

## 2. Build Graph Flow

This is what happens when you run:

```powershell
filegraph --folder ./docs build
```

```mermaid
sequenceDiagram
    participant U as User
    participant CLI as cli.py
    participant Core as FileGraphDB core.py
    participant Scan as scanner.py
    participant Feat as text_features.py
    participant Store as store.py / SQLite

    U->>CLI: filegraph --folder docs build
    CLI->>Core: FileGraphDB(folder).build()
    Core->>Scan: scan_documents(folder)
    Scan-->>Core: list[Document]
    Core->>Feat: TextFeatureIndex(documents)
    Feat-->>Core: keywords, topics, entities, vectors
    Core->>Core: compare document pairs
    Core->>Core: create Edge objects
    Core->>Store: reset()
    Core->>Store: save_documents()
    Core->>Store: save_edges()
    Store-->>Core: .filegraphdb.sqlite
    Core-->>CLI: documents + edge count
    CLI-->>U: built graph summary
```

## 3. Relationship Logic

Each file becomes a `Document` node. FileGraphDB compares each pair of files and creates an `Edge` when the relationship score is strong enough.

```mermaid
flowchart LR
    A[file A text]
    B[file B text]

    A --> Sem[Semantic similarity<br/>LSA or optional sentence-transformers]
    B --> Sem

    A --> Key[Keyword similarity<br/>TF-IDF cosine]
    B --> Key

    A --> Ent[Shared entities<br/>names, dates, emails, URLs]
    B --> Ent

    A --> Top[Shared topics<br/>top TF-IDF terms]
    B --> Top

    A --> Ref[Direct reference<br/>filename/path mention]
    B --> Ref

    Sem --> Score[Hybrid relationship score]
    Key --> Score
    Ent --> Score
    Top --> Score
    Ref --> Score

    Score --> Type{Choose edge type}
    Type --> References[REFERENCES]
    Type --> SharesEntity[SHARES_ENTITY]
    Type --> SharesTopic[SHARES_TOPIC]
    Type --> Similar[SEMANTICALLY_SIMILAR]

    References --> SQLite[(SQLite edges table)]
    SharesEntity --> SQLite
    SharesTopic --> SQLite
    Similar --> SQLite
```

Current formula in `core.py`:

```text
score =
  0.46 * semantic_score
+ 0.24 * keyword_score
+ 0.14 * entity_overlap
+ 0.10 * topic_overlap
+ 0.06 * direct_reference_score
```

## 4. Query / Retrieval Flow

This is what happens when you run:

```powershell
filegraph --folder ./docs search "what caused the project delay"
```

```mermaid
flowchart TD
    Query[User query]
    QueryVectors[Create query semantic + keyword scores]
    Rank[Rank files by query match]
    Seeds[Take top seed files]
    Graph[Expand through graph edges]
    Merge[Merge direct matches + graph neighbors]
    TopK[Return top K files]
    Context[Optional LLM-ready context]

    Query --> QueryVectors
    QueryVectors --> Rank
    Rank --> Seeds
    Seeds --> Graph
    Graph --> Merge
    Seeds --> Merge
    Merge --> TopK
    TopK --> Context
```

The intended LLM usage is:

```mermaid
flowchart LR
    Q[Question]
    FG[FileGraphDB retrieval]
    Few[Only selected files/chunks]
    LLM[LLM]
    Ans[Answer]

    Q --> FG
    FG --> Few
    Few --> LLM
    LLM --> Ans
```

The LLM should not read all files. FileGraphDB selects the likely evidence first.

## 5. SQLite Storage Graph

```mermaid
erDiagram
    NODES {
        text id PK
        text type
        text path
        text content_hash
        integer size
        real modified_time
        text properties_json
    }

    EDGES {
        text id PK
        text source_id FK
        text target_id FK
        text source_path
        text target_path
        text type
        real weight
        real confidence
        text method
        text evidence
        text properties_json
    }

    NODES ||--o{ EDGES : source
    NODES ||--o{ EDGES : target
```

## 6. Evaluation Flow

This is what happens when you run:

```powershell
filegraph --folder ./docs eval samples/eval/politics_guns_eval.jsonl --limit 10
```

```mermaid
flowchart TD
    EvalFile[JSONL eval cases]
    EvalPy[filegraphdb/eval.py]
    Core[filegraphdb/core.py retrieve]
    Results[Selected files]
    Metrics[Metrics]

    EvalFile --> EvalPy
    EvalPy --> Core
    Core --> Results
    Results --> Metrics

    Metrics --> Hit[hit@k]
    Metrics --> MRR[mean reciprocal rank]
    Metrics --> Recall[file recall]
    Metrics --> Terms[answer-term recall]
    Metrics --> Tokens[token savings]
```

## 7. Current Project Layers

```mermaid
flowchart TB
    App[Application Layer<br/>cli.py, test_main.py, scripts/eval_report.py]
    API[Library API Layer<br/>FileGraphDB in core.py]
    Retrieval[Retrieval + Graph Logic<br/>relationship scoring, query ranking, graph expansion]
    Features[Feature Layer<br/>TF-IDF, LSA, entities, topics]
    IO[IO Layer<br/>scanner.py + store.py]
    Data[Data<br/>text files + .filegraphdb.sqlite]

    App --> API
    API --> Retrieval
    Retrieval --> Features
    Retrieval --> IO
    IO --> Data
```

## 8. What Each File Does

| File | Role |
|---|---|
| `filegraphdb/__init__.py` | Public library exports. Lets users write `from filegraphdb import FileGraphDB`. |
| `filegraphdb/core.py` | Main orchestration: build graph, create edges, retrieve files, estimate token savings. |
| `filegraphdb/scanner.py` | Reads folder files, supports extensionless files, cleans newsgroup headers. |
| `filegraphdb/text_features.py` | Extracts features and computes semantic/keyword similarity. |
| `filegraphdb/store.py` | Saves documents and relationships into SQLite. |
| `filegraphdb/models.py` | Defines `Document`, `Edge`, and `SearchResult`. |
| `filegraphdb/cli.py` | Terminal commands: `build`, `search`, `context`, `estimate`, `eval`, `edges`, `related`. |
| `filegraphdb/eval.py` | Evaluates retrieval accuracy using JSONL test cases. |
| `scripts/eval_report.py` | Creates a full Markdown report with queries, evidence, tokens, and costs. |
| `small_llm.py` | Separate small local LLM demo, not part of current graph retrieval pipeline. |
| `test_main.py` | Tiny Python usage example. |

