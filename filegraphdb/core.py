from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np

from .models import Document, Edge, SearchResult
from .scanner import DEFAULT_TEXT_EXTENSIONS, scan_documents
from .store import SQLiteGraphStore
from .text_features import (
    TextFeatureIndex,
    confidence_from_score,
    direct_reference_score,
    jaccard,
)


class FileGraphDB:
    def __init__(
        self,
        folder: str | Path,
        db_path: str | Path | None = None,
        extensions: set[str] | None = None,
        embedding_model: str | None = None,
        use_sentence_transformers: bool = False,
        min_relationship_score: float = 0.25,
        max_edges_per_file: int = 5,
        chunk_word_threshold: int = 2_000,
        chunk_words: int = 800,
        chunk_overlap: int = 120,
    ):
        self.folder = Path(folder).expanduser().resolve()
        self.db_path = Path(db_path) if db_path else self.folder / ".filegraphdb.sqlite"
        self.extensions = extensions or DEFAULT_TEXT_EXTENSIONS
        self.embedding_model = embedding_model
        self.use_sentence_transformers = use_sentence_transformers
        self.min_relationship_score = min_relationship_score
        self.max_edges_per_file = max_edges_per_file
        self.chunk_word_threshold = chunk_word_threshold
        self.chunk_words = chunk_words
        self.chunk_overlap = chunk_overlap
        self.store = SQLiteGraphStore(self.db_path)
        self.documents: list[Document] = []
        self.index: TextFeatureIndex | None = None

    def close(self) -> None:
        self.store.close()

    def __enter__(self) -> "FileGraphDB":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def build(self, reset: bool = True) -> dict:
        documents = self._scan_documents()
        if not documents:
            if reset:
                self.store.reset()
            return {"documents": 0, "edges": 0, "db_path": str(self.db_path)}

        self.index = TextFeatureIndex(
            documents,
            embedding_model=self.embedding_model,
            prefer_sentence_transformers=self.use_sentence_transformers,
        )
        self.documents = self.index.documents
        edges = self._build_relationship_edges()

        if reset:
            self.store.reset()
        self.store.save_documents(self.documents)
        self.store.save_edges(edges)
        return {"documents": len(self.documents), "edges": len(edges), "db_path": str(self.db_path)}

    def related(self, rel_path: str, limit: int = 10) -> list[Edge]:
        normalized = self._normalize_rel_path(rel_path)
        return self.store.edges_for_path(normalized, limit=limit)

    def edges(self, limit: int = 25) -> list[Edge]:
        return self.store.all_edges(limit=limit)

    def retrieve(self, query: str, limit: int = 5, graph_hops: int = 1) -> list[SearchResult]:
        self._ensure_index()
        assert self.index is not None

        semantic_scores, keyword_scores = self.index.query_scores(query)
        base_scores = (0.7 * semantic_scores) + (0.3 * keyword_scores)
        ranked = np.argsort(base_scores)[::-1]

        candidate_scores: dict[str, float] = {}
        reasons: dict[str, str] = {}
        via: dict[str, list[str]] = {}

        seed_count = min(max(limit * 2, 5), len(ranked))
        for idx in ranked:
            if len(candidate_scores) >= seed_count:
                break
            doc = self.documents[int(idx)]
            if not self._is_retrievable_document(doc):
                continue
            score = float(base_scores[int(idx)])
            candidate_scores[doc.id] = max(candidate_scores.get(doc.id, 0.0), score)
            reasons[doc.id] = "query semantic/keyword match"
            via.setdefault(doc.id, [])

            if graph_hops > 0:
                for edge in self.store.edges_for_path(doc.rel_path, limit=self.max_edges_per_file):
                    neighbor_path = edge.target_path if edge.source_path == doc.rel_path else edge.source_path
                    neighbor = self._document_by_path(neighbor_path)
                    if neighbor is None:
                        continue
                    if not self._is_retrievable_document(neighbor):
                        continue
                    expanded_score = score * (0.55 + 0.45 * edge.weight)
                    if expanded_score > candidate_scores.get(neighbor.id, 0.0):
                        candidate_scores[neighbor.id] = expanded_score
                        reasons[neighbor.id] = f"graph expansion through {doc.rel_path}"
                        via[neighbor.id] = [doc.rel_path, edge.type]

        results = [
            SearchResult(
                document=self._document_by_id(doc_id),
                score=score,
                reason=reasons[doc_id],
                via=tuple(via.get(doc_id, [])),
            )
            for doc_id, score in candidate_scores.items()
        ]
        return sorted(results, key=lambda result: result.score, reverse=True)[:limit]

    def context_for_query(self, query: str, limit: int = 5, max_chars_per_file: int = 4000) -> str:
        parts = []
        for result in self.retrieve(query, limit=limit):
            text = result.document.text[:max_chars_per_file]
            parts.append(
                f"--- {result.document.rel_path} | score={result.score:.3f} | {result.reason} ---\n{text}"
            )
        return "\n\n".join(parts)

    def estimate_token_savings(
        self,
        query: str,
        limit: int = 5,
        max_chars_per_file: int | None = None,
        price_per_million_input_tokens: float | None = None,
    ) -> dict:
        self._ensure_index()
        selected = self.retrieve(query, limit=limit)

        all_chars = sum(len(doc.text) for doc in self._source_documents())
        selected_chars = sum(
            len(_clip_text(result.document.text, max_chars_per_file)) for result in selected
        )
        all_tokens = estimate_tokens(all_chars)
        selected_tokens = estimate_tokens(selected_chars)
        saved_tokens = max(0, all_tokens - selected_tokens)
        saved_percent = 0.0 if all_tokens == 0 else saved_tokens / all_tokens * 100.0

        estimate = {
            "query": query,
            "total_documents": len(self.documents),
            "selected_documents": len(selected),
            "selected_paths": [result.document.rel_path for result in selected],
            "all_docs_tokens": all_tokens,
            "filegraph_tokens": selected_tokens,
            "saved_tokens": saved_tokens,
            "saved_percent": round(saved_percent, 2),
            "token_estimator": "rough chars/4 input-token estimate",
        }
        if price_per_million_input_tokens is not None:
            all_cost = all_tokens / 1_000_000 * price_per_million_input_tokens
            selected_cost = selected_tokens / 1_000_000 * price_per_million_input_tokens
            estimate.update(
                {
                    "price_per_million_input_tokens": price_per_million_input_tokens,
                    "all_docs_cost": round(all_cost, 8),
                    "filegraph_cost": round(selected_cost, 8),
                    "saved_cost": round(all_cost - selected_cost, 8),
                }
            )
        return estimate
    def _build_relationship_edges(self) -> list[Edge]:
        assert self.index is not None
        docs = self.documents
        semantic = self.index.semantic_similarity_matrix()
        keyword = self.index.keyword_similarity_matrix()
        outgoing: dict[str, list[Edge]] = {doc.id: [] for doc in docs}
        contains_edges = self._build_contains_edges()

        for left_index, left in enumerate(docs):
            for right_index in range(left_index + 1, len(docs)):
                right = docs[right_index]
                if left.node_type != right.node_type:
                    continue
                forward_ref, forward_evidence = direct_reference_score(left, right)
                backward_ref, backward_evidence = direct_reference_score(right, left)
                direct_ref = max(forward_ref, backward_ref)
                entity_overlap = jaccard(left.entities, right.entities)
                topic_overlap = jaccard(left.topics, right.topics)
                semantic_score = float(semantic[left_index, right_index])
                keyword_score = float(keyword[left_index, right_index])

                score = (
                    0.46 * semantic_score
                    + 0.24 * keyword_score
                    + 0.14 * entity_overlap
                    + 0.10 * topic_overlap
                    + 0.06 * direct_ref
                )

                if direct_ref >= 0.9:
                    edge_type = "REFERENCES"
                elif entity_overlap >= 0.25 and semantic_score >= 0.25:
                    edge_type = "SHARES_ENTITY"
                elif topic_overlap >= 0.35:
                    edge_type = "SHARES_TOPIC"
                else:
                    edge_type = "SEMANTICALLY_SIMILAR"

                if score < self.min_relationship_score and direct_ref < 0.65:
                    continue

                evidence = self._relationship_evidence(
                    left,
                    right,
                    semantic_score,
                    keyword_score,
                    entity_overlap,
                    topic_overlap,
                    forward_evidence or backward_evidence,
                )
                edge = Edge(
                    id=_edge_id(left.id, right.id, edge_type),
                    source_id=left.id,
                    target_id=right.id,
                    source_path=left.rel_path,
                    target_path=right.rel_path,
                    type=edge_type,
                    weight=round(score, 4),
                    confidence=round(confidence_from_score(score), 4),
                    method="hybrid:semantic+tfidf+entities+topics+references",
                    evidence=evidence,
                    properties={
                        "layer": left.node_type,
                        "semantic_score": round(semantic_score, 4),
                        "keyword_score": round(keyword_score, 4),
                        "entity_overlap": round(entity_overlap, 4),
                        "topic_overlap": round(topic_overlap, 4),
                        "direct_reference": round(direct_ref, 4),
                    },
                )
                outgoing[left.id].append(edge)
                outgoing[right.id].append(edge)

        selected: dict[str, Edge] = {}
        for edge in contains_edges:
            selected[edge.id] = edge
        for edges in outgoing.values():
            for edge in sorted(edges, key=lambda item: item.weight, reverse=True)[: self.max_edges_per_file]:
                selected[edge.id] = edge
        return sorted(selected.values(), key=lambda edge: edge.weight, reverse=True)

    def _build_contains_edges(self) -> list[Edge]:
        edges = []
        for doc in self.documents:
            if doc.node_type != "Chunk" or not doc.parent_id or not doc.parent_path:
                continue
            edges.append(
                Edge(
                    id=_edge_id(doc.parent_id, doc.id, "CONTAINS"),
                    source_id=doc.parent_id,
                    target_id=doc.id,
                    source_path=doc.parent_path,
                    target_path=doc.rel_path,
                    type="CONTAINS",
                    weight=1.0,
                    confidence=1.0,
                    method="scanner:chunking",
                    evidence=f"{doc.parent_path} contains {doc.rel_path}",
                    properties={
                        "parent_path": doc.parent_path,
                        "chunk_index": doc.chunk_index,
                        "start_word": doc.start_word,
                        "end_word": doc.end_word,
                    },
                )
            )
        return edges

    def _relationship_evidence(
        self,
        left: Document,
        right: Document,
        semantic_score: float,
        keyword_score: float,
        entity_overlap: float,
        topic_overlap: float,
        direct_evidence: str,
    ) -> str:
        shared_topics = sorted(set(left.topics) & set(right.topics))[:5]
        shared_entities = sorted(set(left.entities) & set(right.entities))[:5]
        pieces = [
            f"semantic={semantic_score:.3f}",
            f"keyword={keyword_score:.3f}",
            f"topic_overlap={topic_overlap:.3f}",
            f"entity_overlap={entity_overlap:.3f}",
        ]
        if shared_topics:
            pieces.append("shared_topics=" + ", ".join(shared_topics))
        if shared_entities:
            pieces.append("shared_entities=" + ", ".join(shared_entities))
        if direct_evidence:
            pieces.append(direct_evidence)
        return "; ".join(pieces)

    def _ensure_index(self) -> None:
        if self.index is not None and self.documents:
            return
        documents = self._scan_documents()
        self.index = TextFeatureIndex(
            documents,
            embedding_model=self.embedding_model,
            prefer_sentence_transformers=self.use_sentence_transformers,
        )
        self.documents = self.index.documents

    def _scan_documents(self) -> list[Document]:
        return scan_documents(
            self.folder,
            self.extensions,
            chunk_word_threshold=self.chunk_word_threshold,
            chunk_words=self.chunk_words,
            chunk_overlap=self.chunk_overlap,
        )

    def _normalize_rel_path(self, rel_path: str) -> str:
        path = Path(rel_path)
        if path.is_absolute():
            return path.resolve().relative_to(self.folder).as_posix()
        return path.as_posix()

    def _document_by_path(self, rel_path: str) -> Document | None:
        for doc in self.documents:
            if doc.rel_path == rel_path:
                return doc
        return None

    def _document_by_id(self, doc_id: str) -> Document:
        for doc in self.documents:
            if doc.id == doc_id:
                return doc
        raise KeyError(doc_id)

    def _chunked_file_paths(self) -> set[str]:
        return {doc.parent_path for doc in self.documents if doc.node_type == "Chunk" and doc.parent_path}

    def _is_retrievable_document(self, doc: Document) -> bool:
        if doc.node_type == "Chunk":
            return True
        return doc.rel_path not in self._chunked_file_paths()

    def _source_documents(self) -> list[Document]:
        file_docs = [doc for doc in self.documents if doc.node_type == "File"]
        return file_docs or self.documents


def _edge_id(source_id: str, target_id: str, edge_type: str) -> str:
    pair = "|".join(sorted([source_id, target_id]))
    raw = f"{pair}|{edge_type}".encode("utf-8")
    return hashlib.sha1(raw).hexdigest()


def estimate_tokens(char_count: int) -> int:
    return max(1, round(char_count / 4))


def _clip_text(text: str, max_chars: int | None) -> str:
    if max_chars is None:
        return text
    return text[:max_chars]
