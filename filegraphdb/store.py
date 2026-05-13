from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from .models import Document, Edge


class SQLiteGraphStore:
    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._ensure_schema()

    def close(self) -> None:
        self.conn.close()

    def reset(self) -> None:
        self.conn.execute("DELETE FROM edges")
        self.conn.execute("DELETE FROM nodes")
        self.conn.commit()

    def save_documents(self, documents: list[Document]) -> None:
        rows = [
            (
                doc.id,
                doc.node_type,
                doc.rel_path,
                doc.content_hash,
                doc.size,
                doc.modified_time,
                json.dumps(
                    {
                        "node_type": doc.node_type,
                        "parent_id": doc.parent_id,
                        "parent_path": doc.parent_path,
                        "chunk_index": doc.chunk_index,
                        "start_word": doc.start_word,
                        "end_word": doc.end_word,
                        "keywords": list(doc.keywords),
                        "topics": list(doc.topics),
                        "entities": list(doc.entities),
                    },
                    ensure_ascii=True,
                ),
            )
            for doc in documents
        ]
        self.conn.executemany(
            """
            INSERT OR REPLACE INTO nodes
              (id, type, path, content_hash, size, modified_time, properties_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        self.conn.commit()

    def save_edges(self, edges: list[Edge]) -> None:
        rows = [
            (
                edge.id,
                edge.source_id,
                edge.target_id,
                edge.source_path,
                edge.target_path,
                edge.type,
                edge.weight,
                edge.confidence,
                edge.method,
                edge.evidence,
                json.dumps(edge.properties, ensure_ascii=True),
            )
            for edge in edges
        ]
        self.conn.executemany(
            """
            INSERT OR REPLACE INTO edges
              (id, source_id, target_id, source_path, target_path, type, weight,
               confidence, method, evidence, properties_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        self.conn.commit()

    def edges_for_path(self, rel_path: str, limit: int = 10) -> list[Edge]:
        rows = self.conn.execute(
            """
            SELECT * FROM edges
            WHERE source_path = ? OR target_path = ?
            ORDER BY weight DESC
            LIMIT ?
            """,
            (rel_path, rel_path, limit),
        ).fetchall()
        return [_edge_from_row(row) for row in rows]

    def all_edges(self, limit: int | None = None) -> list[Edge]:
        sql = "SELECT * FROM edges ORDER BY weight DESC"
        params: tuple = ()
        if limit is not None:
            sql += " LIMIT ?"
            params = (limit,)
        rows = self.conn.execute(sql, params).fetchall()
        return [_edge_from_row(row) for row in rows]

    def _ensure_schema(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS nodes (
              id TEXT PRIMARY KEY,
              type TEXT NOT NULL,
              path TEXT UNIQUE NOT NULL,
              content_hash TEXT NOT NULL,
              size INTEGER NOT NULL,
              modified_time REAL NOT NULL,
              properties_json TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS edges (
              id TEXT PRIMARY KEY,
              source_id TEXT NOT NULL,
              target_id TEXT NOT NULL,
              source_path TEXT NOT NULL,
              target_path TEXT NOT NULL,
              type TEXT NOT NULL,
              weight REAL NOT NULL,
              confidence REAL NOT NULL,
              method TEXT NOT NULL,
              evidence TEXT NOT NULL,
              properties_json TEXT NOT NULL,
              FOREIGN KEY(source_id) REFERENCES nodes(id),
              FOREIGN KEY(target_id) REFERENCES nodes(id)
            );

            CREATE INDEX IF NOT EXISTS idx_edges_source ON edges(source_path);
            CREATE INDEX IF NOT EXISTS idx_edges_target ON edges(target_path);
            CREATE INDEX IF NOT EXISTS idx_edges_type ON edges(type);
            """
        )
        self.conn.commit()


def _edge_from_row(row: sqlite3.Row) -> Edge:
    return Edge(
        id=row["id"],
        source_id=row["source_id"],
        target_id=row["target_id"],
        source_path=row["source_path"],
        target_path=row["target_path"],
        type=row["type"],
        weight=float(row["weight"]),
        confidence=float(row["confidence"]),
        method=row["method"],
        evidence=row["evidence"],
        properties=json.loads(row["properties_json"]),
    )
