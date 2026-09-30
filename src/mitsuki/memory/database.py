import sqlite3
from pathlib import Path
from typing import List, Dict, Optional

class MemoryManager:
    def __init__(self, db_path: str = "data/mitsuki.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database tables for conversation history and long-term facts."""
        with sqlite3.connect(self.db_path) as conn:
            # Raw message log table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Structured long-term facts / memory table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS facts (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def save_message(self, role: str, content: str) -> None:
        """Save a single chat message to persistent storage."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO messages (role, content) VALUES (?, ?)",
                (role, content)
            )
            conn.commit()

    def load_history(self, limit: int = 50) -> List[Dict[str, str]]:
        """Load recent conversation history for context injection."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT role, content FROM messages ORDER BY id DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
            
        return [{"role": row[0], "content": row[1]} for row in reversed(rows)]

    def set_fact(self, key: str, value: str) -> None:
        """Store or update a long-term fact about the user or relationship."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO facts (key, value, updated_at) 
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(key) DO UPDATE SET 
                    value = excluded.value,
                    updated_at = CURRENT_TIMESTAMP
            """, (key, value))
            conn.commit()

    def get_all_facts(self) -> Dict[str, str]:
        """Retrieve all stored long-term facts."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM facts")
            rows = cursor.fetchall()
        return {row[0]: row[1] for row in rows}

    def clear_history(self) -> None:
        """Clear conversation message history."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM messages")
            conn.commit()

    def clear_all(self) -> None:
        """Wipe both messages and structured facts."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM messages")
            conn.execute("DELETE FROM facts")
            conn.commit()