from __future__ import annotations

import math
import re
from dataclasses import replace
from pathlib import Path

import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize

from .models import Document


ENTITY_RE = re.compile(
    r"(?u)\b(?:[A-Z][A-Za-z0-9&.\-]{2,})(?:\s+(?:[A-Z][A-Za-z0-9&.\-]{2,})){0,4}\b"
)
DATE_RE = re.compile(r"\b(?:\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{2,4})\b")
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b")
URL_RE = re.compile(r"https?://[^\s)>\]]+")
TOKEN_RE = re.compile(r"(?u)\b[a-zA-Z][a-zA-Z0-9_\-]{2,}\b")
ENTITY_STOPWORDS = {
    "A",
    "An",
    "And",
    "As",
    "At",
    "But",
    "For",
    "From",
    "He",
    "Her",
    "His",
    "If",
    "In",
    "It",
    "Its",
    "No",
    "Not",
    "Of",
    "On",
    "Or",
    "She",
    "That",
    "The",
    "Their",
    "Then",
    "There",
    "They",
    "This",
    "To",
    "Was",
    "Were",
    "With",
}


class TextFeatureIndex:
    def __init__(
        self,
        documents: list[Document],
        embedding_model: str | None = None,
        prefer_sentence_transformers: bool = True,
    ):
        self.embedding_model = embedding_model or "sentence-transformers/all-MiniLM-L6-v2"
        self._st_model = None
        self.documents = documents
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.95,
            sublinear_tf=True,
        )
        try:
            self.tfidf = self.vectorizer.fit_transform([doc.text for doc in documents])
        except ValueError:
            self.vectorizer = TfidfVectorizer(
                lowercase=True,
                stop_words=None,
                ngram_range=(1, 2),
                min_df=1,
                sublinear_tf=True,
            )
            self.tfidf = self.vectorizer.fit_transform([doc.text for doc in documents])
        self.feature_names = np.asarray(self.vectorizer.get_feature_names_out())
        self.embeddings = self._build_semantic_vectors(prefer_sentence_transformers)
        self.documents = self._attach_extracted_features()
        self.id_to_index = {doc.id: index for index, doc in enumerate(self.documents)}

    def semantic_similarity_matrix(self) -> np.ndarray:
        return cosine_similarity(self.embeddings)

    def keyword_similarity_matrix(self) -> np.ndarray:
        return cosine_similarity(self.tfidf)

    def query_scores(self, query: str) -> tuple[np.ndarray, np.ndarray]:
        query_tfidf = self.vectorizer.transform([query])
        keyword_scores = cosine_similarity(query_tfidf, self.tfidf)[0]

        if self._st_model is not None:
            query_embedding = self._st_model.encode([query], normalize_embeddings=True)
        else:
            query_embedding = self._lsa_query_vector(query_tfidf)
        semantic_scores = cosine_similarity(query_embedding, self.embeddings)[0]
        return semantic_scores, keyword_scores

    def _build_semantic_vectors(self, prefer_sentence_transformers: bool) -> np.ndarray:
        if prefer_sentence_transformers:
            try:
                from sentence_transformers import SentenceTransformer

                self._st_model = SentenceTransformer(self.embedding_model)
                return np.asarray(
                    self._st_model.encode(
                        [doc.text for doc in self.documents],
                        normalize_embeddings=True,
                        show_progress_bar=False,
                    )
                )
            except Exception:
                self._st_model = None

        return self._build_lsa_vectors()

    def _build_lsa_vectors(self) -> np.ndarray:
        rows, cols = self.tfidf.shape
        max_components = max(1, min(128, rows - 1, cols - 1))
        if max_components < 2:
            dense = self.tfidf.toarray()
            return normalize(dense)

        self._svd = TruncatedSVD(n_components=max_components, random_state=42)
        reduced = self._svd.fit_transform(self.tfidf)
        return normalize(reduced)

    def _lsa_query_vector(self, query_tfidf) -> np.ndarray:
        if hasattr(self, "_svd"):
            return normalize(self._svd.transform(query_tfidf))
        return normalize(query_tfidf.toarray())

    def _attach_extracted_features(self) -> list[Document]:
        updated: list[Document] = []
        for index, doc in enumerate(self.documents):
            keywords = self._top_terms(index, limit=12)
            entities = tuple(sorted(extract_entities(doc.text))[:30])
            topics = tuple(keywords[:6])
            updated.append(replace(doc, keywords=keywords, topics=topics, entities=entities))
        return updated

    def _top_terms(self, row_index: int, limit: int) -> tuple[str, ...]:
        row = self.tfidf.getrow(row_index)
        if row.nnz == 0:
            return ()
        top_positions = np.argsort(row.data)[-limit:][::-1]
        terms = self.feature_names[row.indices[top_positions]]
        return tuple(str(term) for term in terms)


def extract_entities(text: str) -> set[str]:
    entities = set()
    entities.update(match.group(0).strip() for match in ENTITY_RE.finditer(text))
    entities.update(match.group(0).strip() for match in DATE_RE.finditer(text))
    entities.update(match.group(0).strip() for match in EMAIL_RE.finditer(text))
    entities.update(match.group(0).strip() for match in URL_RE.finditer(text))
    return {
        entity
        for entity in entities
        if len(entity) > 2 and entity not in ENTITY_STOPWORDS
    }


def jaccard(left: set[str] | tuple[str, ...], right: set[str] | tuple[str, ...]) -> float:
    left_set = set(left)
    right_set = set(right)
    if not left_set or not right_set:
        return 0.0
    return len(left_set & right_set) / len(left_set | right_set)


def direct_reference_score(source: Document, target: Document) -> tuple[float, str]:
    text = source.text.lower()
    target_path = target.rel_path.lower()
    target_name = Path(target.rel_path).name.lower()
    target_stem = Path(target.rel_path).stem.lower()

    if target_path in text:
        return 1.0, f"mentions path '{target.rel_path}'"
    if target_name in text:
        return 0.9, f"mentions filename '{target_name}'"
    if target_stem and re.search(rf"(?<!\w){re.escape(target_stem)}(?!\w)", text):
        return 0.65, f"mentions file stem '{target_stem}'"
    return 0.0, ""


def confidence_from_score(score: float) -> float:
    return 1.0 / (1.0 + math.exp(-8.0 * (score - 0.5)))
