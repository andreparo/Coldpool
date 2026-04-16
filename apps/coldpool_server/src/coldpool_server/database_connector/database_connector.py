from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any


class DatabaseConnector:
    """Simple SQLite connector for the Coldpool project database."""

    DATABASE_FILE_NAME = "coldpool_database.sqlite"

    @classmethod
    def _get_database_path(cls) -> Path:
        """
        Return the configured database path.

        Priority:
        1. COLDPOOL_DATABASE_PATH environment variable
        2. Current working directory / coldpool_database.sqlite
        """
        configured_path = os.environ.get("COLDPOOL_DATABASE_PATH")
        if configured_path is not None and configured_path.strip():
            return Path(configured_path).expanduser()

        return Path.cwd() / cls.DATABASE_FILE_NAME

    @classmethod
    def execute_query(cls, query: str, params: list[Any]) -> list[sqlite3.Row]:
        """
        Execute a SQL query against the Coldpool SQLite database.

        Args:
            query: SQL query string.
            params: Query parameters in positional order.

        Returns:
            A list of sqlite3.Row objects. For non-SELECT queries,
            this will usually be an empty list.

        Raises:
            FileNotFoundError: If the database file does not exist.
            sqlite3.Error: If the SQLite operation fails.
            ValueError: If the query is empty.
        """
        if not query or not query.strip():
            raise ValueError("Query must not be empty.")

        database_path = cls._get_database_path()
        if not database_path.exists():
            raise FileNotFoundError(f"Coldpool database file not found: {database_path}")

        connection = sqlite3.connect(database_path)
        connection.row_factory = sqlite3.Row

        try:
            cursor = connection.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            connection.commit()
            return rows
        except sqlite3.Error:
            connection.rollback()
            raise
        finally:
            connection.close()
