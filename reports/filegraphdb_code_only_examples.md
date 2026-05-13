```powershell
pip install -U filegraphdb
```

```powershell
pip install -U "filegraphdb[models]"
```

```powershell
mkdir demo_docs
Set-Content demo_docs\project_timeline.txt "The product launch was delayed because the vendor shipment arrived late. The engineering team moved the beta release to Friday."
Set-Content demo_docs\vendor_delay.txt "The vendor reported a shipment delay for the beta hardware. This delay affected the launch timeline."
Set-Content demo_docs\budget_notes.txt "The budget review approved extra spending for testing, support, and deployment."
Set-Content demo_docs\garden_plan.txt "The garden plan includes tomatoes, basil, and irrigation setup for the weekend."
```

```python
from filegraphdb import FileGraphDB

graph = FileGraphDB("./demo_docs")
summary = graph.build()

print(summary)
```

```python
from filegraphdb import FileGraphDB

graph = FileGraphDB("./demo_docs")
graph.build()

results = graph.retrieve("what caused the launch delay?", limit=3)

for result in results:
    print(result.document.rel_path, round(result.score, 3), result.reason)
```

```python
from filegraphdb import FileGraphDB

graph = FileGraphDB("./demo_docs")
graph.build()

context = graph.context_for_query("what caused the launch delay?", limit=2)

print(context)
```

```python
from filegraphdb import FileGraphDB

graph = FileGraphDB("./demo_docs")
graph.build()

edges = graph.edges(limit=10)

for edge in edges:
    print(edge.source_path, edge.type, edge.target_path, edge.weight)
```

```python
from filegraphdb import FileGraphDB

graph = FileGraphDB("./demo_docs")
graph.build()

related = graph.related("project_timeline.txt", limit=5)

for edge in related:
    print(edge.source_path, edge.type, edge.target_path, edge.weight)
    print(edge.evidence)
```

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

```powershell
filegraph --folder ./demo_docs build
```

```powershell
filegraph --folder ./demo_docs search "what caused the launch delay?" --limit 3
```

```powershell
filegraph --folder ./demo_docs context "what caused the launch delay?" --limit 2
```

```powershell
filegraph --folder ./demo_docs edges --limit 10
```

```powershell
filegraph --folder ./demo_docs related project_timeline.txt --limit 5
```

```powershell
filegraph --folder ./demo_docs estimate "what caused the launch delay?" --limit 2 --price-per-million 0.15
```

```powershell
filegraph --folder ./demo_docs visualize --out demo_graph.html
```

```powershell
filegraph --folder ./demo_docs build --min-score 0.2 --max-edges 10
```

```powershell
filegraph --folder ./demo_docs --chunk-threshold 2000 --chunk-words 800 --chunk-overlap 120 build
```

```powershell
filegraph --folder ./demo_docs --use-model build
```

```powershell
@'
{"query":"what caused the launch delay?","expected_files":["vendor_delay.txt","project_timeline.txt"],"expected_terms":["vendor","shipment","delay","launch"]}
{"query":"what document talks about garden planning?","expected_files":["garden_plan.txt"],"expected_terms":["garden","tomatoes","irrigation"]}
'@ | Set-Content demo_eval.jsonl
```

```powershell
filegraph --folder ./demo_docs eval demo_eval.jsonl --limit 3 --show-cases
```

```python
from pathlib import Path
from filegraphdb import FileGraphDB

folder = Path("./demo_docs")

graph = FileGraphDB(folder)
graph.build()

queries = [
    "what caused the launch delay?",
    "which notes mention the vendor?",
    "what document talks about garden planning?",
    "what is related to the budget review?",
]

for query in queries:
    print()
    print("QUERY:", query)
    results = graph.retrieve(query, limit=3)
    for result in results:
        print(result.document.rel_path, round(result.score, 3))
```

```python
from filegraphdb import FileGraphDB

graph = FileGraphDB("./demo_docs")
graph.build()

query = "what caused the launch delay?"
context = graph.context_for_query(query, limit=3)

prompt = f"""
Use only this context to answer the question.

Context:
{context}

Question:
{query}
"""

print(prompt)
```

```python
from filegraphdb import FileGraphDB

graph = FileGraphDB("./demo_docs")
graph.build()

results = graph.retrieve("what caused the launch delay?", limit=3)

for index, result in enumerate(results, start=1):
    doc = result.document
    print(f"{index}. {doc.rel_path}")
    print(f"score: {result.score:.3f}")
    print(f"type: {doc.node_type}")
    print(f"keywords: {doc.keywords}")
    print(f"topics: {doc.topics}")
    print(f"entities: {doc.entities}")
    print()
```

```python
from filegraphdb import FileGraphDB

graph = FileGraphDB("./demo_docs")
graph.build()

for edge in graph.edges(limit=20):
    print(
        {
            "source": edge.source_path,
            "target": edge.target_path,
            "type": edge.type,
            "weight": edge.weight,
            "confidence": edge.confidence,
            "method": edge.method,
            "evidence": edge.evidence,
        }
    )
```

```powershell
mkdir relationship_demo
Set-Content relationship_demo\53294.txt "The writer argues that handgun restrictions reduce public safety because lawful citizens lose the ability to defend themselves. The message discusses waiting periods, defensive gun use, and crime deterrence."
Set-Content relationship_demo\53318.txt "This document supports the same argument as 53294. It says that gun control laws mostly affect lawful owners, while criminals ignore restrictions. It also mentions defensive gun use and deterrence."
Set-Content relationship_demo\53372.txt "The author discusses handgun bans, self defense, and crime deterrence. The document argues that armed citizens can prevent crime and that restrictions may punish responsible owners."
Set-Content relationship_demo\54000.txt "This document argues the opposite view. It says handgun restrictions and waiting periods may reduce violence and accidental shootings."
Set-Content relationship_demo\budget.txt "The team budget includes cloud hosting, software licenses, and customer support allocation."
Set-Content relationship_demo\garden.txt "The garden plan includes basil, tomatoes, irrigation, compost, and weekend planting."
```

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

```python
from filegraphdb import FileGraphDB

graph = FileGraphDB("./relationship_demo", min_relationship_score=0.2, max_edges_per_file=10)
graph.build()

queries = [
    # Plain RAG can answer direct questions well.
    "what does file 53294 argue?",

    # FileGraphDB is useful here because the user asks for related documents, not only direct text matches.
    "which documents support the same argument as file 53294?",

    # FileGraphDB is useful here because it can use file-to-file relationships and shared topics.
    "find files connected to 53294 through self defense, handgun restrictions, or deterrence",

    # FileGraphDB is useful here because opposite/similar documents may sit near the same topic area.
    "which documents discuss the opposite side of the handgun restriction argument?",

    # FileGraphDB is useful here because it can surface a neighborhood of related files for investigation.
    "show me the document cluster around handgun laws and public safety",
]

for query in queries:
    print()
    print("QUERY:", query)
    for result in graph.retrieve(query, limit=4, graph_hops=1):
        print(result.document.rel_path, round(result.score, 3), result.reason, result.via)
```

```python
from filegraphdb import FileGraphDB

graph = FileGraphDB("./relationship_demo", min_relationship_score=0.2, max_edges_per_file=10)
graph.build()

file_to_check = "53294.txt"

print("RELATED FILES FOR:", file_to_check)

for edge in graph.related(file_to_check, limit=10):
    other_file = edge.target_path if edge.source_path == file_to_check else edge.source_path
    print()
    print("file:", other_file)
    print("relationship:", edge.type)
    print("weight:", edge.weight)
    print("confidence:", edge.confidence)
    print("evidence:", edge.evidence)
```

```python
from filegraphdb import FileGraphDB

graph = FileGraphDB("./relationship_demo", min_relationship_score=0.2, max_edges_per_file=10)
graph.build()

query = "which documents support the same argument as file 53294?"

print("TOKEN SAVING ESTIMATE")
print(graph.estimate_token_savings(query, limit=4, price_per_million_input_tokens=0.15))

print()
print("LLM CONTEXT")
print(graph.context_for_query(query, limit=4))
```

```python
from filegraphdb import FileGraphDB
from filegraphdb.visualize import visualize_graph

graph = FileGraphDB(
    "./relationship_demo",
    min_relationship_score=0.2,
    max_edges_per_file=10,
)

graph.build()

result = visualize_graph(
    folder="./relationship_demo",
    out_path="relationship_demo_graph.html",
    limit_edges=100,
    min_weight=0.0,
)

print(result)
```

```powershell
filegraph --folder ./relationship_demo build --min-score 0.2 --max-edges 10
```

```powershell
filegraph --folder ./relationship_demo related 53294.txt --limit 10
```

```powershell
filegraph --folder ./relationship_demo search "which documents support the same argument as file 53294?" --limit 5
```

```powershell
filegraph --folder ./relationship_demo context "which documents support the same argument as file 53294?" --limit 5
```

```powershell
filegraph --folder ./relationship_demo estimate "which documents support the same argument as file 53294?" --limit 5 --price-per-million 0.15
```

```powershell
filegraph --folder ./relationship_demo visualize --out relationship_demo_graph.html --limit-edges 100 --min-weight 0.0
```

```python
from filegraphdb import FileGraphDB

folder = "./your_real_docs"

graph = FileGraphDB(
    folder,
    min_relationship_score=0.25,
    max_edges_per_file=8,
    chunk_word_threshold=2000,
    chunk_words=800,
    chunk_overlap=120,
)

graph.build()

relationship_queries = [
    "which documents support the same argument as file X?",
    "which files are related to this report?",
    "which documents mention the same people, companies, or events?",
    "which files share the same topic but use different words?",
    "which documents are in the same evidence cluster?",
    "which documents should I read together?",
    "which documents reference the same policy or decision?",
    "which files discuss the same incident from different angles?",
    "which documents are similar to this file but not exact duplicates?",
    "which files connect this issue to another issue?",
]

for query in relationship_queries:
    print()
    print("QUERY:", query)
    for result in graph.retrieve(query, limit=5, graph_hops=1):
        print(result.document.rel_path, round(result.score, 3), result.reason, result.via)
```

```python
from filegraphdb import FileGraphDB

folder = "./your_real_docs"
target_file = "replace_this_with_real_file_name.txt"

graph = FileGraphDB(folder, min_relationship_score=0.25, max_edges_per_file=10)
graph.build()

print("GRAPH NEIGHBORHOOD")
for edge in graph.related(target_file, limit=15):
    neighbor = edge.target_path if edge.source_path == target_file else edge.source_path
    print(neighbor, edge.type, edge.weight, edge.evidence)
```

```python
from filegraphdb import FileGraphDB

folder = "./your_real_docs"

graph = FileGraphDB(folder, min_relationship_score=0.25, max_edges_per_file=10)
graph.build()

direct_question = "what caused the launch delay?"
relationship_question = "which documents support the same argument as the launch delay report?"

print("DIRECT QUESTION")
for result in graph.retrieve(direct_question, limit=5, graph_hops=0):
    print(result.document.rel_path, round(result.score, 3), result.reason)

print()
print("RELATIONSHIP QUESTION")
for result in graph.retrieve(relationship_question, limit=5, graph_hops=1):
    print(result.document.rel_path, round(result.score, 3), result.reason, result.via)
```

```text
FileGraphDB advantage query types:

1. Which documents support the same argument as file X?
2. Which documents disagree with file X but discuss the same topic?
3. Which files are related to this file through shared entities?
4. Which files are related to this file through shared topics?
5. Which chunks belong to this large file?
6. Which chunks from different files discuss the same idea?
7. Which files should be read together before answering?
8. Which documents form the evidence cluster for this claim?
9. Which files mention the same person, company, law, event, or product?
10. Which documents reference this file by name?
11. Which files are semantically similar but do not share exact keywords?
12. Which files contain duplicate or near-duplicate arguments?
13. Which documents connect topic A to topic B?
14. Which files explain the background around this document?
15. Which related files can reduce LLM context size for this question?
```

```text
Normal RAG strong query types:

1. What is the answer to this direct question?
2. Which chunk contains this exact fact?
3. Summarize the most relevant passages for this query.
4. Find documents that match these keywords.
5. Retrieve top chunks by embedding similarity.
```

```text
FileGraphDB is more useful when the question is about relationships.

Examples:

Query: which documents support the same argument as file 53294?
Reason: the answer depends on file-to-file similarity and graph edges.

Query: which documents should I read together?
Reason: the answer depends on clusters, not one isolated chunk.

Query: what other files discuss this same issue using different words?
Reason: semantic edges can find related files even when keywords differ.

Query: show the graph around this policy document.
Reason: visualization can show connected files, edge types, and evidence.

Query: which chunks from long reports are related to each other?
Reason: chunk nodes avoid sending the whole 10000-word document to the LLM.
```
