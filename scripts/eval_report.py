from __future__ import annotations

import argparse
from pathlib import Path

from filegraphdb import FileGraphDB
from filegraphdb.eval import evaluate_retrieval, load_eval_cases


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder", required=True)
    parser.add_argument("--eval-file", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--price-per-million", type=float, default=0.15)
    parser.add_argument("--max-answer-chars", type=int, default=900)
    args = parser.parse_args()

    graph = FileGraphDB(args.folder)
    cases = load_eval_cases(args.eval_file)
    report = evaluate_retrieval(graph, cases, limit=args.limit)

    lines = [
        "# FileGraphDB Evaluation Report",
        "",
        f"Folder: `{args.folder}`",
        f"Eval file: `{args.eval_file}`",
        f"Limit: `{args.limit}`",
        f"Input token price used: `${args.price_per_million}` per 1M input tokens",
        "",
        "## Summary",
        "",
        f"- Cases: {report['cases']}",
        f"- Hit@K: {_fmt(report['hit_at_k'])}",
        f"- MRR: {_fmt(report['mean_reciprocal_rank'])}",
        f"- Mean file recall: {_fmt(report['mean_file_recall'])}",
        f"- Mean answer-term recall: {_fmt(report['mean_term_recall'])}",
        f"- Mean token savings: {_fmt(report['mean_token_savings_percent'])}%",
        "",
    ]

    rows_by_query = {row["query"]: row for row in report["rows"]}
    for index, case in enumerate(cases, start=1):
        row = rows_by_query[case.query]
        estimate = graph.estimate_token_savings(
            case.query,
            limit=args.limit,
            price_per_million_input_tokens=args.price_per_million,
        )
        results = graph.retrieve(case.query, limit=args.limit)
        evidence = _build_evidence(results, case.expected_terms, args.max_answer_chars)

        lines.extend(
            [
                f"## Case {index}",
                "",
                f"Query: `{case.query}`",
                "",
                "Expected files:",
                "",
                _list_or_none(row["expected_files"]),
                "",
                "Selected files:",
                "",
                _list_or_none(row["selected_files"]),
                "",
                "Matched expected files:",
                "",
                _list_or_none(row["matched_files"]),
                "",
                f"Rank of first expected file: `{row['rank']}`",
                f"File recall: `{_fmt(row['file_recall'])}`",
                f"Matched answer terms: `{', '.join(row['matched_terms']) or '(none)'}`",
                f"Answer-term recall: `{_fmt(row['term_recall'])}`",
                "",
                "Token and cost comparison:",
                "",
                f"- All-docs input tokens: `{estimate['all_docs_tokens']}`",
                f"- FileGraphDB input tokens: `{estimate['filegraph_tokens']}`",
                f"- Saved input tokens: `{estimate['saved_tokens']}`",
                f"- Saved percent: `{estimate['saved_percent']}%`",
                f"- All-docs estimated cost: `${estimate['all_docs_cost']}`",
                f"- FileGraphDB estimated cost: `${estimate['filegraph_cost']}`",
                f"- Estimated saved cost: `${estimate['saved_cost']}`",
                "",
                "Evidence answer preview:",
                "",
                evidence,
                "",
            ]
        )

    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {output}")


def _build_evidence(results, expected_terms: tuple[str, ...], max_chars: int) -> str:
    terms = [term.lower() for term in expected_terms]
    snippets = []
    for result in results:
        text = result.document.text
        lowered = text.lower()
        if terms and not any(term in lowered for term in terms):
            continue
        snippet = " ".join(text.split())[:max_chars]
        snippets.append(f"- `{result.document.rel_path}` score={result.score:.3f}: {snippet}")
        if len(snippets) >= 3:
            break
    return "\n".join(snippets) if snippets else "- No direct expected-term evidence found."


def _list_or_none(items: list[str]) -> str:
    if not items:
        return "- `(none)`"
    return "\n".join(f"- `{item}`" for item in items)


def _fmt(value) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


if __name__ == "__main__":
    main()
