from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .core import FileGraphDB


@dataclass(frozen=True)
class EvalCase:
    query: str
    expected_files: tuple[str, ...]
    expected_terms: tuple[str, ...]


def load_eval_cases(path: str | Path) -> list[EvalCase]:
    cases: list[EvalCase] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            query = data.get("query")
            if not query:
                raise ValueError(f"Missing query at line {line_number}")
            cases.append(
                EvalCase(
                    query=query,
                    expected_files=tuple(data.get("expected_files", [])),
                    expected_terms=tuple(data.get("expected_terms", [])),
                )
            )
    return cases


def evaluate_retrieval(graph: FileGraphDB, cases: list[EvalCase], limit: int = 5) -> dict:
    rows = []
    hit_count = 0
    reciprocal_ranks = []
    file_recalls = []
    term_recalls = []
    saved_percents = []

    for case in cases:
        results = graph.retrieve(case.query, limit=limit)
        selected_paths = [result.document.rel_path for result in results]
        selected_text = "\n".join(result.document.text for result in results).lower()

        expected_files = set(case.expected_files)
        selected_set = set(selected_paths)
        matched_files = sorted(expected_files & selected_set)
        hit = bool(matched_files) if expected_files else None
        if hit:
            hit_count += 1

        rank = None
        for index, path in enumerate(selected_paths, start=1):
            if path in expected_files:
                rank = index
                reciprocal_ranks.append(1 / index)
                break
        if rank is None and expected_files:
            reciprocal_ranks.append(0.0)

        file_recall = None
        if expected_files:
            file_recall = len(matched_files) / len(expected_files)
            file_recalls.append(file_recall)

        expected_terms = [term.lower() for term in case.expected_terms]
        matched_terms = [term for term in expected_terms if term in selected_text]
        term_recall = None
        if expected_terms:
            term_recall = len(matched_terms) / len(expected_terms)
            term_recalls.append(term_recall)

        savings = graph.estimate_token_savings(case.query, limit=limit)
        saved_percents.append(float(savings["saved_percent"]))

        rows.append(
            {
                "query": case.query,
                "selected_files": selected_paths,
                "expected_files": list(case.expected_files),
                "matched_files": matched_files,
                "hit": hit,
                "rank": rank,
                "file_recall": file_recall,
                "expected_terms": list(case.expected_terms),
                "matched_terms": matched_terms,
                "term_recall": term_recall,
                "saved_percent": savings["saved_percent"],
            }
        )

    cases_with_files = sum(1 for case in cases if case.expected_files)
    return {
        "cases": len(cases),
        "limit": limit,
        "hit_at_k": _safe_div(hit_count, cases_with_files),
        "mean_reciprocal_rank": _mean(reciprocal_ranks),
        "mean_file_recall": _mean(file_recalls),
        "mean_term_recall": _mean(term_recalls),
        "mean_token_savings_percent": _mean(saved_percents),
        "rows": rows,
    }


def _mean(values: list[float]) -> float | None:
    if not values:
        return None
    return round(sum(values) / len(values), 4)


def _safe_div(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return round(numerator / denominator, 4)
