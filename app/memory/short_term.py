import time
from typing import Any, Dict, List, Optional
from collections import defaultdict
from app.memory.base import BaseMemory, MemoryItem

class ShortTermMemory(BaseMemory):
    """
    Short-Term Working Memory untuk sesi aktif agen.
    Menyimpan context window, log pemikiran sementara (scratchpad), dan riwayat interaksi.
    """
    def __init__(self, max_items_per_session: int = 20):
        self._storage: Dict[str, List[MemoryItem]] = defaultdict(list)
        self.max_items = max_items_per_session

    async def store(self, key: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        session_id = (metadata or {}).get("session_id", "default")
        item = MemoryItem(
            key=key,
            content=content,
            metadata=metadata or {},
            timestamp=time.time()
        )
        self._storage[session_id].append(item)
        if len(self._storage[session_id]) > self.max_items:
            self._storage[session_id].pop(0)

    async def retrieve(self, query: str, limit: int = 5, session_id: str = "default") -> List[MemoryItem]:
        items = self._storage.get(session_id, [])
        if not query:
            return items[-limit:]
        
        # Simple keyword matching for in-memory context
        query_words = set(query.lower().split())
        matched = []
        for it in items:
            it_words = set(it.content.lower().split())
            overlap = len(query_words.intersection(it_words))
            matched.append((overlap, it))
            
        matched.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in matched[:limit]]

    async def get_session_history(self, session_id: str = "default") -> List[MemoryItem]:
        return self._storage.get(session_id, [])

    async def clear(self, session_id: Optional[str] = None) -> None:
        if session_id:
            if session_id in self._storage:
                del self._storage[session_id]
        else:
            self._storage.clear()
