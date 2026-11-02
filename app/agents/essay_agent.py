import logging
from typing import Any, Dict, Optional
from app.agents.base_agent import BaseAgent
from app.workflow.state import AgentRole

logger = logging.getLogger("jarvis.agents.essay")

class EssayAgent(BaseAgent):
    """
    Spesialis penulisan karya ilmiah, esai mendalam, dan analisis komprehensif.
    Menerapkan pipeline multi-tahap: Outline -> Context Synthesis -> Academic Drafting.
    """
    def __init__(self):
        super().__init__(name="EssayCraftAgent", role=AgentRole.ESSAY)

    async def execute(self, payload: Dict[str, Any], context: Optional[str] = None) -> Dict[str, Any]:
        topic = payload.get("topic") or payload.get("raw_prompt", "Esai Akademis")
        research_notes = payload.get("research_notes", context or "")
        tone = payload.get("tone", "Akademis, terstruktur, mendalam, dan objektif")

        # Tahap 1: Pembentukan Kerangka / Outline
        outline_prompt = f"""
        Topik: {topic}
        Gaya Bahasa: {tone}
        Catatan Riset: {research_notes}

        Susunlah outline esai terstruktur yang mencakup:
        1. Pendahuluan & Latar Belakang Masalah (dengan Thesis Statement yang jelas)
        2. Tinjauan Teoretis / Kerangka Konseptual
        3. Analisis Utama & Argumen Kritis
        4. Implikasi Praktis & Tantangan Implementasi
        5. Kesimpulan & Rekomendasi
        """
        outline = await self.call_llm(
            "Anda adalah Senior Academic Writer. Buatlah outline esai yang sangat solid, logis, dan mendalam.",
            outline_prompt
        )

        # Tahap 2: Penulisan Draf Esai Penuh
        draft_prompt = f"""
        Berdasarkan outline berikut:
        {outline}

        Dan bahan pengayaan / riset:
        {research_notes}

        Tuliskan esai lengkap dalam format Markdown. Pastikan setiap paragraf kaya akan argumen ilmiah, transisi antar bagian mulus, dan tidak ada pengulangan kata yang tidak perlu.
        """
        full_essay = await self.call_llm(
            "Anda adalah Professor & Editor Jurnal Ilmiah bereputasi tinggi. Tulis esai dengan bahasa formal dan berbobot.",
            draft_prompt
        )

        words = len(full_essay.split())

        return {
            "topic": topic,
            "outline": outline.strip(),
            "essay": full_essay.strip(),
            "word_count": words
        }
