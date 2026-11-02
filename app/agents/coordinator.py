import json
import logging
from typing import Any, Dict, Optional
from app.agents.base_agent import BaseAgent
from app.workflow.state import ExecutionPlan, SubTask, AgentRole

logger = logging.getLogger("jarvis.agents.coordinator")

class CoordinatorAgent(BaseAgent):
    """
    Task Router & Orchestration Coordinator (JARVIS Central Controller).
    Bertanggung jawab menerima instruksi dan memecahnya menjadi rencana eksekusi terstruktur.
    """
    def __init__(self):
        super().__init__(name="JarvisCoordinator", role=AgentRole.COORDINATOR)

    async def execute(self, payload: Dict[str, Any], context: Optional[str] = None) -> Dict[str, Any]:
        user_prompt = payload.get("user_input", "")
        plan = await self.decompose_and_route(user_prompt, context)
        return {"plan": plan.model_dump()}

    async def decompose_and_route(self, user_prompt: str, context: Optional[str] = None) -> ExecutionPlan:
        system_instruction = """
        Anda adalah Central Task Coordinator & Router (JARVIS).
        Tugas Anda:
        1. Analisis tujuan utama input user (apakah soal pilihan ganda / kuis, penulisan esai, pembuatan kode program, atau riset data).
        2. Tentukan agen spesialis yang tepat:
           - 'quiz': Untuk soal Pilihan Ganda (PG), problem solving analitis beropsi.
           - 'essay': Untuk esai ilmiah, artikel mendalam, telaah literatur.
           - 'research': Untuk ekstraksi informasi, ringkasan dokumen, atau pencarian fakta pendukung.
           - 'coding': Untuk penulisan fungsi/kode, debugging, atau testing algoritma.
        3. Rancang daftar sub-tugas (subtasks) beserta input data spesifik untuk masing-masing agen.
        4. Tentukan apakah eksekusi sub-tugas dapat dijalankan secara paralel (`requires_parallel`: true/false).

        WAJIB kembalikan respon dalam format JSON:
        {
          "task_goal": "Ringkasan tujuan utama yang ingin dicapai",
          "requires_parallel": false,
          "subtasks": [
            {
              "id": "task_1",
              "target_agent": "quiz" | "essay" | "research" | "coding",
              "description": "Deskripsi singkat sub-tugas",
              "input_data": {
                 // data relevan untuk agen target
              }
            }
          ]
        }
        """

        prompt = f"Instruksi Pengguna:\n{user_prompt}\n\nKonteks Tambahan / Riwayat:\n{context or 'Tidak ada'}"
        raw_output = await self.call_llm(system_instruction, prompt)
        parsed = self.parse_json_safely(raw_output)

        subtasks = []
        for item in parsed.get("subtasks", []):
            try:
                target_agent = AgentRole(item.get("target_agent", "research"))
            except ValueError:
                target_agent = AgentRole.RESEARCH

            # Pastikan input_data memiliki referensi ke teks asli jika kosong
            input_data = item.get("input_data", {})
            if not input_data:
                input_data = {"raw_prompt": user_prompt}

            subtasks.append(SubTask(
                id=item.get("id", f"task_{len(subtasks)+1}"),
                target_agent=target_agent,
                description=item.get("description", "Eksekusi sub-tugas"),
                input_data=input_data
            ))

        if not subtasks:
            # Fallback jika model gagal merinci subtask
            subtasks.append(SubTask(
                id="default_task",
                target_agent=AgentRole.RESEARCH,
                description="Analisis dan eksekusi instruksi pengguna",
                input_data={"raw_prompt": user_prompt}
            ))

        return ExecutionPlan(
            task_goal=parsed.get("task_goal", user_prompt[:100]),
            subtasks=subtasks,
            requires_parallel=parsed.get("requires_parallel", False)
        )
