from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .core import FileGraphDB
from .eval import evaluate_retrieval, load_eval_cases
from .visualize import visualize_graph


def main() -> None:
    _configure_stdout()
    parser = argparse.ArgumentParser(prog="filegraph")
    parser.add_argument("--folder", default=".", help="Folder to scan or query.")
    parser.add_argument("--db", default=None, help="SQLite graph path. Defaults to .filegraphdb.sqlite.")
    parser.add_argument(
        "--use-model",
        action="store_true",
        help="Use sentence-transformers embeddings if installed. Otherwise uses local LSA vectors.",
    )
    parser.add_argument(
        "--chunk-threshold",
        type=int,
        default=2000,
        help="Split files above this many words into chunks. Use 0 to disable chunking.",
    )
    parser.add_argument("--chunk-words", type=int, default=800, help="Words per chunk for long files.")
    parser.add_argument("--chunk-overlap", type=int, default=120, help="Word overlap between chunks.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser("build", help="Scan files and build relationships.")
    build_parser.add_argument("--min-score", type=float, default=0.25)
    build_parser.add_argument("--max-edges", type=int, default=5)

    related_parser = subparsers.add_parser("related", help="Show files related to a file.")
    related_parser.add_argument("path")
    related_parser.add_argument("--limit", type=int, default=10)

    search_parser = subparsers.add_parser("search", help="Retrieve relevant files for a query.")
    search_parser.add_argument("query")
    search_parser.add_argument("--limit", type=int, default=5)

    context_parser = subparsers.add_parser("context", help="Print LLM-ready context for a query.")
    context_parser.add_argument("query")
    context_parser.add_argument("--limit", type=int, default=5)

    estimate_parser = subparsers.add_parser(
        "estimate",
        help="Estimate token savings for all-docs prompting vs FileGraphDB retrieval.",
    )
    estimate_parser.add_argument("query")
    estimate_parser.add_argument("--limit", type=int, default=5)
    estimate_parser.add_argument(
        "--price-per-million",
        type=float,
        default=None,
        help="Optional input-token price to estimate cost, e.g. 0.15 for $0.15 per 1M tokens.",
    )

    eval_parser = subparsers.add_parser(
        "eval",
        help="Evaluate retrieval accuracy using a JSONL file with expected files or terms.",
    )
    eval_parser.add_argument("eval_file")
    eval_parser.add_argument("--limit", type=int, default=5)
    eval_parser.add_argument("--show-cases", action="store_true")

    visualize_parser = subparsers.add_parser(
        "visualize",
        help="Create an interactive HTML node/edge visualization of the graph.",
    )
    visualize_parser.add_argument("--out", default="filegraph_visual.html")
    visualize_parser.add_argument("--limit-edges", type=int, default=300)
    visualize_parser.add_argument("--min-weight", type=float, default=0.0)

    edges_parser = subparsers.add_parser("edges", help="Show strongest graph edges.")
    edges_parser.add_argument("--limit", type=int, default=20)

    args = parser.parse_args()
    graph = FileGraphDB(
        Path(args.folder),
        db_path=args.db,
        use_sentence_transformers=args.use_model,
        min_relationship_score=getattr(args, "min_score", 0.25),
        max_edges_per_file=getattr(args, "max_edges", 5),
        chunk_word_threshold=args.chunk_threshold if args.chunk_threshold > 0 else 10**12,
        chunk_words=args.chunk_words,
        chunk_overlap=args.chunk_overlap,
    )

    if args.command == "build":
        result = graph.build()
        print(f"built graph: documents={result['documents']} edges={result['edges']} db={result['db_path']}")
    elif args.command == "related":
        for edge in graph.related(args.path, limit=args.limit):
            print(_format_edge(edge))
    elif args.command == "search":
        for result in graph.retrieve(args.query, limit=args.limit):
            print(f"{result.score:.3f}  {result.document.rel_path}  {result.reason}")
    elif args.command == "context":
        print(graph.context_for_query(args.query, limit=args.limit))
    elif args.command == "estimate":
        estimate = graph.estimate_token_savings(
            args.query,
            limit=args.limit,
            price_per_million_input_tokens=args.price_per_million,
        )
        print(f"query: {estimate['query']}")
        print(f"documents: all={estimate['total_documents']} selected={estimate['selected_documents']}")
        print(f"selected: {', '.join(estimate['selected_paths'])}")
        print(f"all-docs input tokens: {estimate['all_docs_tokens']}")
        print(f"filegraph input tokens: {estimate['filegraph_tokens']}")
        print(f"saved input tokens: {estimate['saved_tokens']} ({estimate['saved_percent']}%)")
        if args.price_per_million is not None:
            print(f"all-docs cost: ${estimate['all_docs_cost']}")
            print(f"filegraph cost: ${estimate['filegraph_cost']}")
            print(f"saved cost: ${estimate['saved_cost']}")
        print(f"note: {estimate['token_estimator']}")
    elif args.command == "eval":
        cases = load_eval_cases(args.eval_file)
        report = evaluate_retrieval(graph, cases, limit=args.limit)
        print(f"cases: {report['cases']}")
        print(f"limit: {report['limit']}")
        print(f"hit@k: {_format_metric(report['hit_at_k'])}")
        print(f"MRR: {_format_metric(report['mean_reciprocal_rank'])}")
        print(f"mean file recall: {_format_metric(report['mean_file_recall'])}")
        print(f"mean answer-term recall: {_format_metric(report['mean_term_recall'])}")
        print(f"mean token savings: {_format_metric(report['mean_token_savings_percent'])}%")
        if args.show_cases:
            for row in report["rows"]:
                print("")
                print(f"query: {row['query']}")
                print(f"selected: {', '.join(row['selected_files'])}")
                if row["expected_files"]:
                    print(f"expected: {', '.join(row['expected_files'])}")
                    print(f"matched: {', '.join(row['matched_files']) or '(none)'}")
                    print(f"rank: {row['rank']}")
                if row["expected_terms"]:
                    print(f"matched terms: {', '.join(row['matched_terms']) or '(none)'}")
                print(f"term recall: {_format_metric(row['term_recall'])}")
                print(f"token savings: {row['saved_percent']}%")
    elif args.command == "visualize":
        result = visualize_graph(
            folder=args.folder,
            db_path=args.db,
            out_path=args.out,
            limit_edges=args.limit_edges,
            min_weight=args.min_weight,
        )
        print(f"wrote {result['out_path']}")
        print(f"nodes={result['nodes']} edges={result['edges']}")
    elif args.command == "edges":
        for edge in graph.edges(limit=args.limit):
            print(_format_edge(edge))


def _format_edge(edge) -> str:
    return (
        f"{edge.weight:.3f}  {edge.source_path} --{edge.type}--> "
        f"{edge.target_path}  [{edge.evidence}]"
    )


def _format_metric(value) -> str:
    if value is None:
        return "n/a"
    return f"{value:.4f}" if isinstance(value, float) else str(value)


def _configure_stdout() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")


if __name__ == "__main__":
    main()
