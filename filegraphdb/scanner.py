from __future__ import annotations

import hashlib
import re
from pathlib import Path

from .models import Document


DEFAULT_TEXT_EXTENSIONS = {
    "",
    ".txt",
    ".md",
    ".rst",
    ".log",
    ".csv",
    ".json",
    ".yaml",
    ".yml",
}
DEFAULT_CHUNK_WORD_THRESHOLD = 2_000
DEFAULT_CHUNK_WORDS = 800
DEFAULT_CHUNK_OVERLAP = 120
WORD_RE = re.compile(r"\S+")


def scan_documents(
    folder: str | Path,
    extensions: set[str] | None = None,
    max_bytes: int = 2_000_000,
    chunk_word_threshold: int = DEFAULT_CHUNK_WORD_THRESHOLD,
    chunk_words: int = DEFAULT_CHUNK_WORDS,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[Document]:
    root = Path(folder).expanduser().resolve()
    allowed = {ext.lower() for ext in (extensions or DEFAULT_TEXT_EXTENSIONS)}
    documents: list[Document] = []

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.name.startswith(".filegraphdb"):
            continue
        if path.suffix.lower() not in allowed:
            continue
        if path.stat().st_size > max_bytes:
            continue

        text = _clean_newsgroup_text(_read_text(path))
        if not text.strip():
            continue

        rel_path = path.relative_to(root).as_posix()
        raw_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        stat = path.stat()
        file_id = _stable_doc_id(rel_path, raw_hash)
        documents.append(
            Document(
                id=file_id,
                path=path,
                rel_path=rel_path,
                text=text,
                content_hash=raw_hash,
                size=stat.st_size,
                modified_time=stat.st_mtime,
                node_type="File",
            )
        )
        chunks = _chunk_text_if_needed(
            text,
            chunk_word_threshold=chunk_word_threshold,
            chunk_words=chunk_words,
            chunk_overlap=chunk_overlap,
        )
        for chunk in chunks:
            if chunk["index"] is None:
                continue
            chunk_rel_path = f"{rel_path}#chunk-{chunk['index']:04d}"
            chunk_hash = hashlib.sha256(chunk["text"].encode("utf-8")).hexdigest()
            documents.append(
                Document(
                    id=_stable_doc_id(chunk_rel_path, chunk_hash),
                    path=path,
                    rel_path=chunk_rel_path,
                    text=chunk["text"],
                    content_hash=chunk_hash,
                    size=len(chunk["text"].encode("utf-8")),
                    modified_time=stat.st_mtime,
                    node_type="Chunk",
                    parent_id=file_id,
                    parent_path=rel_path,
                    chunk_index=chunk["index"],
                    start_word=chunk["start_word"],
                    end_word=chunk["end_word"],
                )
            )

    return documents


def _read_text(path: Path) -> str:
    data = path.read_bytes()
    for encoding in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def _clean_newsgroup_text(text: str) -> str:
    lines = text.splitlines()
    header_lines = lines[:40]
    header_names = {line.split(":", 1)[0].lower() for line in header_lines if ":" in line}
    looks_like_newsgroup = (
        "subject" in header_names
        and ("from" in header_names or "newsgroups" in header_names or "message-id" in header_names)
    )
    if not looks_like_newsgroup:
        return text

    split_at = None
    for index, line in enumerate(lines):
        if not line.strip():
            split_at = index
            break
    if split_at is None:
        return text

    subject = ""
    for line in lines[:split_at]:
        if line.lower().startswith("subject:"):
            subject = line.strip()
            break
    body = "\n".join(lines[split_at + 1 :]).strip()
    if subject and body:
        return f"{subject}\n\n{body}"
    return body or text


def _chunk_text_if_needed(
    text: str,
    chunk_word_threshold: int,
    chunk_words: int,
    chunk_overlap: int,
) -> list[dict]:
    words = list(WORD_RE.finditer(text))
    if len(words) <= chunk_word_threshold:
        return [{"index": None, "text": text, "start_word": 0, "end_word": len(words)}]
    if chunk_words <= 0:
        return [{"index": None, "text": text, "start_word": 0, "end_word": len(words)}]

    overlap = max(0, min(chunk_overlap, chunk_words - 1))
    step = chunk_words - overlap
    chunks = []
    start = 0
    chunk_index = 1

    while start < len(words):
        end = min(start + chunk_words, len(words))
        start_char = words[start].start()
        end_char = words[end - 1].end()
        chunk_text = text[start_char:end_char].strip()
        if chunk_text:
            chunks.append(
                {
                    "index": chunk_index,
                    "text": chunk_text,
                    "start_word": start,
                    "end_word": end,
                }
            )
            chunk_index += 1
        if end == len(words):
            break
        start += step

    return chunks or [{"index": None, "text": text, "start_word": 0, "end_word": len(words)}]


def _stable_doc_id(rel_path: str, content_hash: str) -> str:
    raw = f"{rel_path}\0{content_hash}".encode("utf-8")
    return hashlib.sha1(raw).hexdigest()
