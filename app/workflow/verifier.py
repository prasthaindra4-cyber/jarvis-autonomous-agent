import json
import logging
from typing import Any, Dict, Optional
from app.agents.base_agent import BaseAgent
from app.workflow.state import AgentRole, VerificationResult

logger = logging.getLogger("jarvis.workflow.verifier")

class VerifierAgent(BaseAgent):
    """
    Quality Assurance & Self-Reflection Agent.
    Memeriksa luaran dari specialized agents, mendeteksi cacat logika, halusinasi, atau inkonsistensi,
    dan memberikan skor serta feedback perbaikan.
    """
    def __init__(self):
        super().__init__(name="QualityVerifierAgent", role=AgentRole.VERIFIER)

    async def execute(self, payload: Dict[str, Any], context: Optional[str] = None) -> Dict[str, Any]:
        goal = payload.get("goal", "")
        results = payload.get("results", {})
        verif = await self.verify(goal, results)
        return verif.model_dump()

    async def verify(self, original_goal: str, intermediate_results: Dict[str, Any]) -> VerificationResult:
        system_instruction = """
        Anda adalah Auditor Mutu & Verifikator Logika Tertinggi (Quality Assurance Agent).
        Tugas Anda memeriksa hasil kerja agen spesialis:
        1. Apakah output secara langsung menjawab tujuan awal (original goal)?
        2. Pada soal PG: Apakah ada opsi yang dipilih dan evaluasi logikanya konsisten?
        3. Pada esai: Apakah strukturnya lengkap dan berbobot?
        4. Pada kode program: Apakah kode valid dan bebas dari cacat sintaks?

        Format Output WAJIB JSON:
        {
          "is_passed": true/false,
          "score": 0.0 sampai 1.0,
          "critique": "Kritik membangun jika ada kekurangan, atau pujian jika sempurna",
          "suggested_fix": "Instruksi spesifik perbaikan jika is_passed adalah false, atau null jika lolos"
        }
        """

        prompt = f"""
        Tujuan Awal Tugas:
        {original_goal}

        Hasil Kerja Agen yang Harus Diverifikasi:
        {json.dumps(intermediate_results, indent=2)}
        """

        raw_output = await self.call_llm(system_instruction, prompt)
        parsed = self.parse_json_safely(raw_output)

        return VerificationResult(
            is_passed=parsed.get("is_passed", True),
            score=float(parsed.get("score", 1.0)),
            critique=parsed.get("critique", "Hasil terverifikasi memenuhi standar."),
            suggested_fix=parsed.get("suggested_fix")
        )
