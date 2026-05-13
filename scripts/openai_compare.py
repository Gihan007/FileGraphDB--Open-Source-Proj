from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from time import perf_counter

from openai import OpenAI

from filegraphdb import FileGraphDB
from filegraphdb.core import estimate_tokens
from filegraphdb.scanner import scan_documents


DEFAULT_MODEL = "gpt-5-nano"
DEFAULT_INPUT_PRICE = 0.05
DEFAULT_OUTPUT_PRICE = 0.40


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare normal all-document LLM answering against FileGraphDB-selected context."
    )
    parser.add_argument("--folder", required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--out", default="reports/openai_comparison_report.md")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--limit", type=int, default=10, help="Number of FileGraphDB documents to send.")
    parser.add_argument("--max-chars-per-file", type=int, default=4000)
    parser.add_argument("--input-price-per-million", type=float, default=DEFAULT_INPUT_PRICE)
    parser.add_argument("--output-price-per-million", type=float, default=DEFAULT_OUTPUT_PRICE)
    parser.add_argument(
        "--allow-large-normal",
        action="store_true",
        help="Actually send the all-documents prompt even when the rough estimate is very large.",
    )
    parser.add_argument(
        "--large-normal-token-threshold",
        type=int,
        default=120_000,
        help="Skip normal all-docs API call above this estimated input size unless --allow-large-normal is set.",
    )
    args = parser.parse_args()

    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is not set. Set it in your shell before running this script.")

    folder = Path(args.folder).expanduser().resolve()
    graph = FileGraphDB(folder)
    build_result = graph.build()

    docs = scan_documents(folder)
    all_context = _all_docs_context(docs, args.max_chars_per_file)
    filegraph_context = graph.context_for_query(
        args.query,
        limit=args.limit,
        max_chars_per_file=args.max_chars_per_file,
    )

    normal_estimated_input_tokens = estimate_tokens(len(_prompt(args.query, all_context)))
    filegraph_estimated_input_tokens = estimate_tokens(len(_prompt(args.query, filegraph_context)))

    client = OpenAI()

    normal_result = None
    normal_skipped_reason = None
    if (
        normal_estimated_input_tokens > args.large_normal_token_threshold
        and not args.allow_large_normal
    ):
        normal_skipped_reason = (
            f"Skipped real normal all-docs call because estimated input tokens "
            f"({normal_estimated_input_tokens}) exceed threshold "
            f"({args.large_normal_token_threshold}). Rerun with --allow-large-normal to force it."
        )
    else:
        normal_result = _call_openai(client, args.model, args.query, all_context)

    filegraph_result = _call_openai(client, args.model, args.query, filegraph_context)

    report = _build_report(
        folder=folder,
        query=args.query,
        model=args.model,
        build_result=build_result,
        limit=args.limit,
        max_chars_per_file=args.max_chars_per_file,
        normal_result=normal_result,
        normal_skipped_reason=normal_skipped_reason,
        normal_estimated_input_tokens=normal_estimated_input_tokens,
        filegraph_result=filegraph_result,
        filegraph_estimated_input_tokens=filegraph_estimated_input_tokens,
        input_price=args.input_price_per_million,
        output_price=args.output_price_per_million,
        selected_paths=[result.document.rel_path for result in graph.retrieve(args.query, limit=args.limit)],
    )

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report, encoding="utf-8")
    print(f"wrote {out}")


def _all_docs_context(docs, max_chars_per_file: int) -> str:
    parts = []
    for doc in docs:
        text = doc.text[:max_chars_per_file]
        parts.append(f"--- {doc.rel_path} ---\n{text}")
    return "\n\n".join(parts)


def _prompt(query: str, context: str) -> str:
    return (
        "Answer the question using only the provided documents. "
        "If the documents do not contain enough evidence, say that. "
        "Cite filenames from the context.\n\n"
        f"Question: {query}\n\n"
        f"Documents:\n{context}"
    )


def _call_openai(client: OpenAI, model: str, query: str, context: str) -> dict:
    prompt = _prompt(query, context)
    start = perf_counter()
    response = client.responses.create(
        model=model,
        input=prompt,
    )
    elapsed = perf_counter() - start
    usage = _usage_dict(response)
    return {
        "answer": getattr(response, "output_text", "").strip(),
        "usage": usage,
        "elapsed_seconds": round(elapsed, 3),
        "estimated_prompt_tokens": estimate_tokens(len(prompt)),
    }


def _usage_dict(response) -> dict:
    usage = getattr(response, "usage", None)
    if usage is None:
        return {}
    if hasattr(usage, "model_dump"):
        return usage.model_dump()
    if isinstance(usage, dict):
        return usage
    return json.loads(json.dumps(usage, default=lambda value: getattr(value, "__dict__", str(value))))


def _build_report(
    *,
    folder: Path,
    query: str,
    model: str,
    build_result: dict,
    limit: int,
    max_chars_per_file: int,
    normal_result: dict | None,
    normal_skipped_reason: str | None,
    normal_estimated_input_tokens: int,
    filegraph_result: dict,
    filegraph_estimated_input_tokens: int,
    input_price: float,
    output_price: float,
    selected_paths: list[str],
) -> str:
    normal_usage = normal_result["usage"] if normal_result else {}
    filegraph_usage = filegraph_result["usage"]

    normal_input_tokens = _usage_value(normal_usage, "input_tokens", normal_estimated_input_tokens)
    normal_output_tokens = _usage_value(normal_usage, "output_tokens", 0)
    filegraph_input_tokens = _usage_value(
        filegraph_usage,
        "input_tokens",
        filegraph_estimated_input_tokens,
    )
    filegraph_output_tokens = _usage_value(filegraph_usage, "output_tokens", 0)

    normal_cost = _cost(normal_input_tokens, normal_output_tokens, input_price, output_price)
    filegraph_cost = _cost(filegraph_input_tokens, filegraph_output_tokens, input_price, output_price)
    saved_input_tokens = max(0, normal_input_tokens - filegraph_input_tokens)
    saved_cost = normal_cost - filegraph_cost
    saved_percent = 0 if normal_input_tokens == 0 else saved_input_tokens / normal_input_tokens * 100

    lines = [
        "# OpenAI Normal vs FileGraphDB Comparison",
        "",
        f"Folder: `{folder}`",
        f"Query: `{query}`",
        f"Model: `{model}`",
        f"Graph build: documents={build_result['documents']} edges={build_result['edges']}",
        f"FileGraphDB selected document limit: `{limit}`",
        f"Max chars per file: `{max_chars_per_file}`",
        f"Input price used: `${input_price}` per 1M tokens",
        f"Output price used: `${output_price}` per 1M tokens",
        "",
        "## Selected FileGraphDB Files",
        "",
        *[f"- `{path}`" for path in selected_paths],
        "",
        "## Token And Cost Summary",
        "",
        "| Method | Input tokens | Output tokens | Estimated cost | Runtime |",
        "|---|---:|---:|---:|---:|",
        _summary_row("Normal all docs", normal_input_tokens, normal_output_tokens, normal_cost, normal_result),
        _summary_row("FileGraphDB", filegraph_input_tokens, filegraph_output_tokens, filegraph_cost, filegraph_result),
        "",
        f"Saved input tokens: `{saved_input_tokens}`",
        f"Saved input percent: `{saved_percent:.2f}%`",
        f"Saved estimated cost: `${saved_cost:.8f}`",
        "",
    ]

    if normal_skipped_reason:
        lines.extend(["## Normal All-Docs Answer", "", normal_skipped_reason, ""])
    else:
        lines.extend(["## Normal All-Docs Answer", "", normal_result["answer"], ""])

    lines.extend(["## FileGraphDB Answer", "", filegraph_result["answer"], ""])
    lines.extend(
        [
            "## Raw Usage",
            "",
            "Normal usage:",
            "",
            f"```json\n{json.dumps(normal_usage, indent=2)}\n```",
            "",
            "FileGraphDB usage:",
            "",
            f"```json\n{json.dumps(filegraph_usage, indent=2)}\n```",
            "",
        ]
    )
    return "\n".join(lines)


def _usage_value(usage: dict, key: str, fallback: int) -> int:
    value = usage.get(key)
    if value is None:
        return fallback
    return int(value)


def _cost(
    input_tokens: int,
    output_tokens: int,
    input_price_per_million: float,
    output_price_per_million: float,
) -> float:
    return (
        input_tokens / 1_000_000 * input_price_per_million
        + output_tokens / 1_000_000 * output_price_per_million
    )


def _summary_row(name: str, input_tokens: int, output_tokens: int, cost: float, result: dict | None) -> str:
    runtime = "skipped" if result is None else f"{result['elapsed_seconds']}s"
    return f"| {name} | {input_tokens} | {output_tokens} | ${cost:.8f} | {runtime} |"


if __name__ == "__main__":
    main()
