# Permite usar anotações de tipo modernas sem avaliá-las imediatamente.
from __future__ import annotations

# Biblioteca padrão usada para criar conexões e executar comandos SQLite.
import sqlite3
# Path permite aceitar caminhos de arquivo como strings ou objetos Path.
from pathlib import Path

# O repositório persiste os resultados produzidos pelo robô.
from .robot import ProtocolResult


class SQLiteStatusRepository:
    """Persiste os status das ocorrências em um banco de dados SQLite."""

    def __init__(self, db_path: str | Path) -> None:
        # SQLite aceita o caminho como texto; a conversão também normaliza objetos Path.
        self._db_path = str(db_path)
        # A tabela é criada automaticamente na primeira utilização do repositório.
        self._ensure_table()

    def _ensure_table(self) -> None:
        """Cria a tabela de protocolos caso ela ainda não exista."""

        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                """
                -- Guarda um histórico de cada tentativa de processamento.
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
        """Insere no banco o resultado de uma ocorrência processada."""

        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                """
                -- Os valores são passados separadamente para evitar SQL construído manualmente.
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

    def list_statuses(self) -> list[ProtocolResult]:
        """Retorna os resultados salvos, do mais recente para o mais antigo."""

        with sqlite3.connect(self._db_path) as conn:
            rows = conn.execute(
                """
                SELECT occurrence_id, status, protocolo, mensagem, timestamp
                FROM rpa_protocolos
                ORDER BY id DESC
                """
            ).fetchall()

        return [
            ProtocolResult(
                occurrence_id=row[0],
                status=row[1],
                protocolo=row[2],
                mensagem=row[3],
                timestamp=row[4],
            )
            for row in rows
        ]
