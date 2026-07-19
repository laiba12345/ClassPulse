from __future__ import annotations

import os
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

DEFAULT_DB = Path(__file__).parents[1] / "data" / "classpulse.db"


class MasteryMemory:
    """Small SQLite repository for mastery state; no model logic lives here."""

    def __init__(self, path: str | Path = DEFAULT_DB):
        self.path = Path(path); self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock(); self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=10)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with closing(self._connect()) as connection:
            with connection:
                connection.execute("""
                CREATE TABLE IF NOT EXISTS mastery_states (
                    student_id TEXT NOT NULL,
                    concept TEXT NOT NULL,
                    mastery REAL NOT NULL,
                    observations INTEGER NOT NULL,
                    correct INTEGER NOT NULL,
                    soft_updates INTEGER NOT NULL,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY (student_id, concept)
                )
                """)

    def load_states(self) -> dict[tuple[str, str], dict]:
        with closing(self._connect()) as connection:
            rows = connection.execute("SELECT * FROM mastery_states").fetchall()
        return {(row["student_id"], row["concept"]): dict(row) for row in rows}

    def save_state(self, student_id: str, concept: str, state) -> None:
        updated_at = datetime.now(timezone.utc).isoformat()
        with self._lock, closing(self._connect()) as connection:
            with connection:
                connection.execute("""
                INSERT INTO mastery_states (student_id, concept, mastery, observations, correct, soft_updates, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(student_id, concept) DO UPDATE SET
                    mastery=excluded.mastery, observations=excluded.observations,
                    correct=excluded.correct, soft_updates=excluded.soft_updates,
                    updated_at=excluded.updated_at
                """, (student_id, concept, state.mastery, state.observations, state.correct, state.soft_updates, updated_at))


def build_memory() -> MasteryMemory | None:
    if os.getenv("CLASSPULSE_MEMORY_MODE", "on").lower() == "off":
        return None
    return MasteryMemory(os.getenv("CLASSPULSE_DB", str(DEFAULT_DB)))
