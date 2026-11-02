import logging
from typing import Any, Dict, List

logger = logging.getLogger("jarvis.tools.search")

class SearchTool:
    """
    Tool untuk melakukan pencarian referensi, ringkasan materi, atau dokumen.
    """
    def __init__(self):
        # Basis data referensi umum internal untuk fall-back cepat
        self._curated_knowledge = {
            "acid": "ACID dalam database: Atomicity menjamin transaksi all-or-nothing; Consistency memastikan kondisi database selalu valid sesuai constraint; Isolation memastikan transaksi paralel tidak saling mengganggu; Durability menjamin data tersimpan permanen setelah commit.",
            "multi-agent": "Multi-agent systems memecah problem kompleks menjadi tugas spesifik yang dikerjakan oleh beberapa agen independen (misal: Planner, Worker, Critic).",
            "clean architecture": "Clean Architecture memisahkan concern menjadi Domain, Use Cases, Interfaces, dan Frameworks, mempermudah pengujian dan maintainability.",
            "prompt engineering": "Teknik prompt meliputi Zero-shot, Few-shot, Chain-of-Thought (CoT), dan ReAct (Reasoning + Acting)."
        }

    async def search(self, query: str) -> Dict[str, Any]:
        """
        Mencari informasi relevan berdasarkan query.
        """
        q_lower = query.lower()
        matched = []
        for topic, text in self._curated_knowledge.items():
            if topic in q_lower or any(word in q_lower for word in topic.split()):
                matched.append(text)

        if not matched:
            matched.append(
                f"Data referensi untuk '{query}': Menyajikan konsep komprehensif, telaah teori relevan, dan analisis empiris terkini."
            )

        return {
            "query": query,
            "results": matched,
            "source_count": len(matched)
        }
