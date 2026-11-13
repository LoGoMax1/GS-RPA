from __future__ import annotations

import sqlite3
from pathlib import Path

from .robot import ProtocolResult


class SQLiteStatusRepository:
    def __init__(self, db_path: str | Path) -> None:
        self._db_path = str(db_path)
        self._ensure_table()

    def _ensure_table(self) -> None:
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS rpa_protocolos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    occurrence_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    protocolo TEXT,
                    mensagem TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
                """
            )

    def save_status(self, result: ProtocolResult) -> None:
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                """
                INSERT INTO rpa_protocolos (occurrence_id, status, protocolo, mensagem, timestamp)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    result.occurrence_id,
                    result.status,
                    result.protocolo,
                    result.mensagem,
                    result.timestamp,
                ),
            )
