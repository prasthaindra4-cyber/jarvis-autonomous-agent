import abc
import json
import logging
from typing import Any, Dict, Optional
from app.core.llm_provider import llm_provider
from app.core.config import settings
from app.workflow.state import AgentRole

logger = logging.getLogger("jarvis.agents")

class BaseAgent(abc.ABC):
    """
    Kelas abstrak untuk seluruh specialized agent di ekosistem JARVIS.
    """
    def __init__(self, name: str, role: AgentRole, model_name: Optional[str] = None):
        self.name = name
        self.role = role
        self.model_name = model_name or settings.GEMINI_MODEL
        self.provider = llm_provider

    @abc.abstractmethod
    async def execute(self, payload: Dict[str, Any], context: Optional[str] = None) -> Dict[str, Any]:
        """
        Menjalankan aksi mandiri agen.
        """
        pass

    async def call_llm(self, system_instruction: str, user_prompt: str, temperature: float = 0.2) -> str:
        """Helper untuk melakukan pemanggilan LLM secara terstandar."""
        return await self.provider.generate(
            system_instruction=system_instruction,
            user_prompt=user_prompt,
            model_name=self.model_name,
            temperature=temperature
        )

    def parse_json_safely(self, text: str) -> Dict[str, Any]:
        """Ekstraksi JSON aman dari output LLM."""
        cleaned = text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned.removeprefix("```json").removesuffix("```").strip()
        elif cleaned.startswith("```"):
            cleaned = cleaned.removeprefix("```").removesuffix("```").strip()
            
        try:
            return json.loads(cleaned)
        except Exception:
            # Fallback jika model menghasilkan teks non-JSON murni
            start = cleaned.find("{")
            end = cleaned.rfind("}")
            if start != -1 and end != -1:
                try:
                    return json.loads(cleaned[start:end+1])
                except Exception:
                    pass
            return {"raw_text": text}
