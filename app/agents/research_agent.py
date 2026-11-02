import logging
from typing import Any, Dict, Optional
from app.agents.base_agent import BaseAgent
from app.workflow.state import AgentRole
from app.tools.search_tool import SearchTool

logger = logging.getLogger("jarvis.agents.research")

class ResearchAgent(BaseAgent):
    """
    Spesialis pencarian referensi, RAG / pencarian dokumen, dan perangkuman materi kredibel.
    """
    def __init__(self):
        super().__init__(name="ResearchAgent", role=AgentRole.RESEARCH)
        self.search_tool = SearchTool()

    async def execute(self, payload: Dict[str, Any], context: Optional[str] = None) -> Dict[str, Any]:
        query = payload.get("query") or payload.get("raw_prompt", "")
        
        # 1. Cari data referensi menggunakan tool
        tool_results = await self.search_tool.search(query)
        tool_context = "\n".join(tool_results.get("results", []))

        # 2. Sintesis hasil menggunakan LLM
        system_instruction = """
        Anda adalah Research & Intelligence Analyst.
        Tugas Anda:
        1. Ekstrak data dan konsep faktual penting dari informasi referensi yang tersedia.
        2. Susun ringkasan temuan kunci (key findings) yang tajam, faktual, dan siap digunakan oleh agen penulis atau pengambil keputusan.
        3. Berikan atribusi referensi konseptual.

        Kembalikan respon JSON:
        {
          "summary": "Ringkasan komprehensif topik",
          "key_findings": ["poin 1", "poin 2", "poin 3"],
          "references": ["referensi 1", "referensi 2"]
        }
        """

        prompt = f"Topik Riset: {query}\n\nFakta / Konteks Ditemukan:\n{tool_context}\n\nKonteks Tambahan:\n{context or 'Tidak ada'}"
        raw_output = await self.call_llm(system_instruction, prompt)
        parsed = self.parse_json_safely(raw_output)
        
        # Sertakan data mentah tool untuk transparansi
        parsed["tool_sources"] = tool_results.get("results", [])
        return parsed
