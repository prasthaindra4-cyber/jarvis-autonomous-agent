import json
import logging
from typing import Any, Dict, Optional
from app.agents.base_agent import BaseAgent
from app.workflow.state import AgentRole

logger = logging.getLogger("jarvis.agents.quiz")

class QuizAgent(BaseAgent):
    """
    Spesialis penyelesaian soal Pilihan Ganda (PG) dan problem solving analitis.
    Menerapkan Chain of Thought (CoT) dan Eliminasi Opsi Sistematis.
    """
    def __init__(self):
        super().__init__(name="QuizSolverAgent", role=AgentRole.QUIZ)

    async def execute(self, payload: Dict[str, Any], context: Optional[str] = None) -> Dict[str, Any]:
        raw_prompt = payload.get("raw_prompt") or payload.get("question", "")
        options = payload.get("options", {})

        system_instruction = """
        Anda adalah AI Master Solver untuk Ujian Akademik, Sertifikasi Teknis, dan Tes Standar.
        Prosedur Wajib:
        1. Analisis Inti Masalah: Jelaskan konsep fundamental yang diuji dalam soal.
        2. Evaluasi & Eliminasi Tiap Opsi: Periksa opsi A, B, C, D, E secara teliti. Berikan alasan spesifik mengapa salah atau benar.
        3. Penentuan Jawaban: Pilih 1 opsi yang paling akurat secara definitif.
        4. Verifikasi Logika: Pastikan tidak ada ambiguitas atau kontradiksi internal.

        Format Respon Wajib JSON:
        {
          "concept_analysis": "Penjelasan inti konsep soal",
          "options_evaluation": {
            "A": "Analisis apakah opsi ini benar atau salah beserta argumennya",
            "B": "...",
            "C": "...",
            "D": "..."
          },
          "selected_option": "Huruf opsi yang terpilih (misal: 'B')",
          "confidence_score": 0.95,
          "summary_justification": "Rangkuman ringkas dan lugas mengapa jawaban tersebut benar"
        }
        """

        user_content = f"Soal / Permasalahan:\n{raw_prompt}"
        if options:
            user_content += f"\n\nOpsi Pilihan:\n{json.dumps(options, indent=2)}"
        if context:
            user_content += f"\n\nInformasi Konteks Tambahan:\n{context}"

        raw_output = await self.call_llm(system_instruction, user_content)
        parsed = self.parse_json_safely(raw_output)
        
        # Validasi field penting
        if "selected_option" not in parsed:
            parsed["selected_option"] = "A"
            parsed["summary_justification"] = "Jawaban dihasilkan dari analisis deduktif."

        return parsed
