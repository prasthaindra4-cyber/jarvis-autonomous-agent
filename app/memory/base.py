import abc
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class MemoryItem(BaseModel):
    key: str
    content: str
    metadata: Dict[str, Any] = {}
    timestamp: float

class BaseMemory(abc.ABC):
    @abc.abstractmethod
    async def store(self, key: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        pass

    @abc.abstractmethod
    async def retrieve(self, query: str, limit: int = 5) -> List[MemoryItem]:
        pass

    @abc.abstractmethod
    async def clear(self, session_id: Optional[str] = None) -> None:
        pass
