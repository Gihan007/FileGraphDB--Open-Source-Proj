from __future__ import annotations

import argparse
from pathlib import Path

from advanced_rag_baseline import AdvancedRAGBaseline
from filegraphdb import FileGraphDB


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare FileGraphDB retrieval against a standard advanced RAG baseline.")
    parser.add_argument("--folder", required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--price-per-million", type=float, default=0.15)
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    filegraph = FileGraphDB(args.folder)
    fg_build = filegraph.build()
    fg_results = filegraph.retrieve(args.query, limit=args.limit)
    fg_estimate = filegraph.estimate_token_savings(
        args.query,
        limit=args.limit,
        price_per_million_input_tokens=args.price_per_million,
    )

    rag = AdvancedRAGBaseline(args.folder)
    rag_build = rag.build()
    rag_results = rag.retrieve(args.query, limit=args.limit)
    rag_estimate = rag.estimate_token_savings(args.query, limit=args.limit)

    lines = [
        "# FileGraphDB vs Advanced RAG Baseline",
        "",
        f"Folder: `{Path(args.folder).resolve()}`",
        f"Query: `{args.query}`",
        f"Limit: `{args.limit}`",
        "",
        "## Build Summary",
        "",
        f"- FileGraphDB documents/chunks: `{fg_build['documents']}`",
        f"- FileGraphDB edges: `{fg_build['edges']}`",
        f"- Advanced RAG chunks: `{rag_build['chunks']}`",
        "",
        "## Token Summary",
        "",
        "| Method | Total tokens | Selected tokens | Saved tokens | Saved percent |",
        "|---|---:|---:|---:|---:|",
        f"| FileGraphDB | {fg_estimate['all_docs_tokens']} | {fg_estimate['filegraph_tokens']} | {fg_estimate['saved_tokens']} | {fg_estimate['saved_percent']}% |",
        f"| Advanced RAG | {rag_estimate['all_chunks_tokens']} | {rag_estimate['rag_tokens']} | {rag_estimate['saved_tokens']} | {rag_estimate['saved_percent']}% |",
        "",
        "## FileGraphDB Results",
        "",
    ]
    lines.extend(
        f"- `{result.document.rel_path}` score={result.score:.3f} reason={result.reason}"
        for result in fg_results
    )
    lines.extend(["", "## Advanced RAG Results", ""])
    lines.extend(
        f"- `{result.document.rel_path}` score={result.score:.3f} semantic={result.semantic_score:.3f} keyword={result.keyword_score:.3f} rerank={result.rerank_score:.3f}"
        for result in rag_results
    )
    lines.extend(["", "## Overlap", ""])
    fg_paths = {_base_path(result.document.rel_path) for result in fg_results}
    rag_paths = {_base_path(result.document.rel_path) for result in rag_results}
    overlap = sorted(fg_paths & rag_paths)
    if overlap:
        lines.extend(f"- `{path}`" for path in overlap)
    else:
        lines.append("- `(none)`")

    report = "\n".join(lines)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report, encoding="utf-8")
        print(f"wrote {out}")
    print(report)


def _base_path(path: str) -> str:
    return path.split("#chunk-", 1)[0]


if __name__ == "__main__":
    main()
