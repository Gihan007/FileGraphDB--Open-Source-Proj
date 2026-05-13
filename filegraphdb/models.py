from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Document:
    id: str
    path: Path
    rel_path: str
    text: str
    content_hash: str
    size: int
    modified_time: float
    node_type: str = "File"
    parent_id: str | None = None
    parent_path: str | None = None
    chunk_index: int | None = None
    start_word: int | None = None
    end_word: int | None = None
    keywords: tuple[str, ...] = ()
    topics: tuple[str, ...] = ()
    entities: tuple[str, ...] = ()


@dataclass(frozen=True)
class Edge:
    id: str
    source_id: str
    target_id: str
    source_path: str
    target_path: str
    type: str
    weight: float
    confidence: float
    method: str
    evidence: str
    properties: dict = field(default_factory=dict)


@dataclass(frozen=True)
class SearchResult:
    document: Document
    score: float
    reason: str
    via: tuple[str, ...] = ()
