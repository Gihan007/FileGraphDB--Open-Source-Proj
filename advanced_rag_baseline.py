from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize

from filegraphdb.core import estimate_tokens
from filegraphdb.models import Document
from filegraphdb.scanner import DEFAULT_TEXT_EXTENSIONS, scan_documents


TOKEN_RE = re.compile(r"(?u)\b[a-zA-Z][a-zA-Z0-9_\-]{2,}\b")


@dataclass(frozen=True)
class RagResult:
    document: Document
    score: float
    semantic_score: float
    keyword_score: float
    rerank_score: float


class AdvancedRAGBaseline:
    """A standard local RAG retriever baseline.

    This intentionally does not use FileGraphDB edges. It represents a common
    advanced RAG retrieval flow:

    files -> chunks -> TF-IDF keyword index -> LSA semantic index -> hybrid ranking -> reranking
    """

    def __init__(
        self,
        folder: str | Path,
        extensions: set[str] | None = None,
        chunk_word_threshold: int = 0,
        chunk_words: int = 450,
        chunk_overlap: int = 80,
        semantic_weight: float = 0.62,
        keyword_weight: float = 0.28,
        rerank_weight: float = 0.10,
    ):
        self.folder = Path(folder).expanduser().resolve()
        self.extensions = extensions or DEFAULT_TEXT_EXTENSIONS
        self.chunk_word_threshold = chunk_word_threshold
        self.chunk_words = chunk_words
        self.chunk_overlap = chunk_overlap
        self.semantic_weight = semantic_weight
        self.keyword_weight = keyword_weight
        self.rerank_weight = rerank_weight
        self.documents: list[Document] = []
        self.vectorizer: TfidfVectorizer | None = None
        self.tfidf = None
        self.embeddings: np.ndarray | None = None
        self._svd: TruncatedSVD | None = None

    def build(self) -> dict:
        scanned = scan_documents(
            self.folder,
            self.extensions,
            chunk_word_threshold=self.chunk_word_threshold,
            chunk_words=self.chunk_words,
            chunk_overlap=self.chunk_overlap,
        )
        chunked_paths = {doc.parent_path for doc in scanned if doc.node_type == "Chunk" and doc.parent_path}
        self.documents = [
            doc for doc in scanned if doc.node_type == "Chunk" or doc.rel_path not in chunked_paths
        ]
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.95,
            sublinear_tf=True,
        )
        try:
            self.tfidf = self.vectorizer.fit_transform([doc.text for doc in self.documents])
        except ValueError:
            self.vectorizer = TfidfVectorizer(
                lowercase=True,
                stop_words=None,
                ngram_range=(1, 2),
                min_df=1,
                sublinear_tf=True,
            )
            self.tfidf = self.vectorizer.fit_transform([doc.text for doc in self.documents])
        self.embeddings = self._build_lsa_vectors()
        return {"documents": len(self.documents), "chunks": len(self.documents)}

    def retrieve(self, query: str, limit: int = 8, candidate_multiplier: int = 6) -> list[RagResult]:
        self._ensure_built()
        assert self.vectorizer is not None
        assert self.tfidf is not None
        assert self.embeddings is not None

        query_tfidf = self.vectorizer.transform([query])
        keyword_scores = cosine_similarity(query_tfidf, self.tfidf)[0]
        query_embedding = self._lsa_query_vector(query_tfidf)
        semantic_scores = cosine_similarity(query_embedding, self.embeddings)[0]

        base_scores = (
            self.semantic_weight * semantic_scores
            + self.keyword_weight * keyword_scores
        )
        candidate_count = min(max(limit * candidate_multiplier, limit), len(self.documents))
        candidate_indexes = np.argsort(base_scores)[::-1][:candidate_count]
        query_terms = _important_query_terms(query)

        results: list[RagResult] = []
        for index in candidate_indexes:
            doc = self.documents[int(index)]
            rerank_score = _query_term_coverage(query_terms, doc.text)
            score = float(base_scores[int(index)] + self.rerank_weight * rerank_score)
            results.append(
                RagResult(
                    document=doc,
                    score=score,
                    semantic_score=float(semantic_scores[int(index)]),
                    keyword_score=float(keyword_scores[int(index)]),
                    rerank_score=rerank_score,
                )
            )

        return sorted(results, key=lambda result: result.score, reverse=True)[:limit]

    def context_for_query(self, query: str, limit: int = 8, max_chars_per_chunk: int = 2200) -> str:
        parts = []
        for result in self.retrieve(query, limit=limit):
            text = result.document.text[:max_chars_per_chunk]
            parts.append(
                f"--- {result.document.rel_path} | score={result.score:.3f} "
                f"| semantic={result.semantic_score:.3f} | keyword={result.keyword_score:.3f} "
                f"| rerank={result.rerank_score:.3f} ---\n{text}"
            )
        return "\n\n".join(parts)

    def estimate_token_savings(self, query: str, limit: int = 8, max_chars_per_chunk: int = 2200) -> dict:
        self._ensure_built()
        selected = self.retrieve(query, limit=limit)
        all_chars = sum(len(doc.text) for doc in self.documents)
        selected_chars = sum(len(result.document.text[:max_chars_per_chunk]) for result in selected)
        all_tokens = estimate_tokens(all_chars)
        selected_tokens = estimate_tokens(selected_chars)
        saved_tokens = max(0, all_tokens - selected_tokens)
        saved_percent = 0.0 if all_tokens == 0 else saved_tokens / all_tokens * 100.0
        return {
            "query": query,
            "total_chunks": len(self.documents),
            "selected_chunks": len(selected),
            "selected_paths": [result.document.rel_path for result in selected],
            "all_chunks_tokens": all_tokens,
            "rag_tokens": selected_tokens,
            "saved_tokens": saved_tokens,
            "saved_percent": round(saved_percent, 2),
        }

    def _build_lsa_vectors(self) -> np.ndarray:
        assert self.tfidf is not None
        rows, cols = self.tfidf.shape
        max_components = max(1, min(192, rows - 1, cols - 1))
        if max_components < 2:
            return normalize(self.tfidf.toarray())
        self._svd = TruncatedSVD(n_components=max_components, random_state=42)
        return normalize(self._svd.fit_transform(self.tfidf))

    def _lsa_query_vector(self, query_tfidf) -> np.ndarray:
        if self._svd is not None:
            return normalize(self._svd.transform(query_tfidf))
        return normalize(query_tfidf.toarray())

    def _ensure_built(self) -> None:
        if not self.documents:
            self.build()


def _important_query_terms(query: str) -> set[str]:
    stopwords = {
        "about",
        "after",
        "and",
        "are",
        "did",
        "for",
        "from",
        "how",
        "the",
        "this",
        "was",
        "what",
        "when",
        "where",
        "which",
        "who",
        "why",
        "with",
    }
    return {match.group(0).lower() for match in TOKEN_RE.finditer(query) if match.group(0).lower() not in stopwords}


def _query_term_coverage(query_terms: set[str], text: str) -> float:
    if not query_terms:
        return 0.0
    lowered = text.lower()
    matched = sum(1 for term in query_terms if term in lowered)
    return matched / len(query_terms)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run an advanced local RAG baseline over a folder.")
    parser.add_argument("--folder", required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--chunk-words", type=int, default=450)
    parser.add_argument("--chunk-overlap", type=int, default=80)
    parser.add_argument("--max-chars-per-chunk", type=int, default=2200)
    parser.add_argument("--context", action="store_true")
    args = parser.parse_args()

    rag = AdvancedRAGBaseline(
        args.folder,
        chunk_words=args.chunk_words,
        chunk_overlap=args.chunk_overlap,
    )
    summary = rag.build()
    print(f"built advanced RAG index: chunks={summary['chunks']}")

    for result in rag.retrieve(args.query, limit=args.limit):
        print(
            f"{result.score:.3f}  {result.document.rel_path}  "
            f"semantic={result.semantic_score:.3f} keyword={result.keyword_score:.3f} rerank={result.rerank_score:.3f}"
        )

    estimate = rag.estimate_token_savings(args.query, limit=args.limit, max_chars_per_chunk=args.max_chars_per_chunk)
    print("")
    print(f"all chunk tokens: {estimate['all_chunks_tokens']}")
    print(f"advanced RAG tokens: {estimate['rag_tokens']}")
    print(f"saved tokens: {estimate['saved_tokens']} ({estimate['saved_percent']}%)")

    if args.context:
        print("")
        print(rag.context_for_query(args.query, limit=args.limit, max_chars_per_chunk=args.max_chars_per_chunk))


if __name__ == "__main__":
    main()
