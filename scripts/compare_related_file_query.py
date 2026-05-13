from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from advanced_rag_baseline import AdvancedRAGBaseline
from filegraphdb import FileGraphDB


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder", required=True)
    parser.add_argument("--file", required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    graph = FileGraphDB(args.folder, min_relationship_score=0.30, max_edges_per_file=8)
    graph_summary = graph.build()
    related_edges = graph.related(args.file, limit=args.limit)

    rag = AdvancedRAGBaseline(args.folder)
    rag_summary = rag.build()
    rag_results = rag.retrieve(args.query, limit=args.limit)

    graph_paths = {
        edge.target_path if edge.source_path == args.file else edge.source_path
        for edge in related_edges
    }
    rag_paths = {result.document.rel_path.split("#chunk-", 1)[0] for result in rag_results}
    overlap = sorted(graph_paths & rag_paths)

    lines = [
        "# FileGraphDB Related-File Query vs Advanced RAG",
        "",
        f"Folder: `{Path(args.folder).resolve()}`",
        f"Question: `{args.query}`",
        f"Start file: `{args.file}`",
        f"Limit: `{args.limit}`",
        "",
        "## Build Summary",
        "",
        f"- FileGraphDB nodes: `{graph_summary['documents']}`",
        f"- FileGraphDB edges: `{graph_summary['edges']}`",
        f"- Advanced RAG chunks: `{rag_summary['chunks']}`",
        "",
        "## FileGraphDB Results",
        "",
        "FileGraphDB treats this as a graph-neighborhood query: `related(file)`.",
        "",
    ]
    for edge in related_edges:
        neighbor = edge.target_path if edge.source_path == args.file else edge.source_path
        lines.append(
            f"- `{neighbor}` score={edge.weight:.3f} type={edge.type} evidence={edge.evidence}"
        )

    lines.extend(
        [
            "",
            "## Advanced RAG Results",
            "",
            "Advanced RAG treats this as a normal text query. It does not know that `53294` should be expanded through graph relationships.",
            "",
        ]
    )
    for result in rag_results:
        lines.append(
            f"- `{result.document.rel_path}` score={result.score:.3f} "
            f"semantic={result.semantic_score:.3f} keyword={result.keyword_score:.3f} rerank={result.rerank_score:.3f}"
        )

    lines.extend(["", "## Overlap", ""])
    if overlap:
        lines.extend(f"- `{path}`" for path in overlap)
    else:
        lines.append("- `(none)`")

    Path(args.out).write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {args.out}")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
