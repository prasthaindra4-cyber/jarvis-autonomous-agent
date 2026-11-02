import sqlite3
import json
import time
from typing import Any, Dict, List, Optional
from app.memory.base import BaseMemory, MemoryItem
from app.core.config import settings

class LongTermMemory(BaseMemory):
    """
    Long-Term Memory tersimpan persisten dalam SQLite.
    Menyimpan ringkasan solusi, knowledge base, dan preferensi lintas sesi.
    """
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.SQLITE_DB_PATH
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS long_term_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    memory_key TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata_json TEXT,
                    timestamp REAL NOT NULL
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_mem_key ON long_term_memory (memory_key)
            """)
            conn.commit()

    async def store(self, key: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        metadata_str = json.dumps(metadata or {})
        now = time.time()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO long_term_memory (memory_key, content, metadata_json, timestamp) VALUES (?, ?, ?, ?)",
                (key, content, metadata_str, now)
            )
            conn.commit()

    async def retrieve(self, query: str, limit: int = 5) -> List[MemoryItem]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Full-text like query search
            search_param = f"%{query}%"
            cursor.execute(
                "SELECT memory_key, content, metadata_json, timestamp FROM long_term_memory "
                "WHERE content LIKE ? OR memory_key LIKE ? ORDER BY timestamp DESC LIMIT ?",
                (search_param, search_param, limit)
            )
            rows = cursor.fetchall()

        results = []
        for r in rows:
            meta = json.loads(r[2]) if r[2] else {}
            results.append(MemoryItem(
                key=r[0],
                content=r[1],
                metadata=meta,
                timestamp=r[3]
            ))
        return results

    async def clear(self, session_id: Optional[str] = None) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM long_term_memory")
            conn.commit()
