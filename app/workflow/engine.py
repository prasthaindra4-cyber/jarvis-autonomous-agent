import asyncio
import logging
from typing import Dict, Any, Optional
from app.workflow.state import (
    AgentWorkflowState,
    TaskStatus,
    AgentRole,
    SubTask,
    ExecutionPlan
)
from app.agents.coordinator import CoordinatorAgent
from app.agents.quiz_agent import QuizAgent
from app.agents.essay_agent import EssayAgent
from app.agents.research_agent import ResearchAgent
from app.agents.coding_agent import CodingAgent
from app.workflow.verifier import VerifierAgent
from app.memory.short_term import ShortTermMemory
from app.memory.long_term import LongTermMemory

logger = logging.getLogger("jarvis.workflow.engine")

class AutonomousWorkflowEngine:
    """
    Mesin Orkestrasi Otonom Utama:
    Mengeksekusi alur Plan -> Execute -> Verify -> Output secara mandiri dan adaptif.
    """
    def __init__(self):
        self.coordinator = CoordinatorAgent()
        self.quiz_agent = QuizAgent()
        self.essay_agent = EssayAgent()
        self.research_agent = ResearchAgent()
        self.coding_agent = CodingAgent()
        self.verifier = VerifierAgent()
        
        # Memory layers
        self.short_term_memory = ShortTermMemory()
        self.long_term_memory = LongTermMemory()

    def _resolve_agent(self, role: AgentRole):
        registry = {
            AgentRole.COORDINATOR: self.coordinator,
            AgentRole.QUIZ: self.quiz_agent,
            AgentRole.ESSAY: self.essay_agent,
            AgentRole.RESEARCH: self.research_agent,
            AgentRole.CODING: self.coding_agent,
            AgentRole.VERIFIER: self.verifier
        }
        return registry.get(role, self.research_agent)

    async def run(self, user_input: str, session_id: str = "default_session") -> AgentWorkflowState:
        """
        Siklus hidup eksekusi penuh otonom.
        """
        state = AgentWorkflowState(session_id=session_id, user_input=user_input)
        state.log(f"Menerima instruksi baru pada sesi: {session_id}")

        # 0. Ambil riwayat memori (Short-Term & Long-Term)
        short_history = await self.short_term_memory.get_session_history(session_id)
        context_str = "\n".join([f"[{m.key}]: {m.content}" for m in short_history[-3:]])
        
        lt_items = await self.long_term_memory.retrieve(user_input[:30], limit=2)
        if lt_items:
            context_str += "\nKnowledge Base Relevan:\n" + "\n".join([f"- {item.content}" for item in lt_items])

        # Simpan input ke short-term memory
        await self.short_term_memory.store("user_prompt", user_input, {"session_id": session_id})

        # --- TAHAP 1: PLAN (Perencanaan & Dekomposisi) ---
        state.status = TaskStatus.PLANNING
        state.log("Menjalankan Coordinator Agent untuk menyusun Execution Plan...")
        plan = await self.coordinator.decompose_and_route(user_input, context_str)
        state.plan = plan
        state.log(f"Plan terbentuk: {len(plan.subtasks)} subtask. Parallel={plan.requires_parallel}")

        # --- LOOP EKSEKUSI & VERIFIKASI (Dengan Self-Correction) ---
        while state.retry_count <= state.max_retries:
            # --- TAHAP 2: EXECUTE (Eksekusi Agen Spesialis) ---
            state.status = TaskStatus.EXECUTING
            state.log(f"Mengeksekusi subtasks (Percobaan ke-{state.retry_count + 1})...")

            if plan.requires_parallel and len(plan.subtasks) > 1:
                # Eksekusi paralel via asyncio.gather
                tasks = [self._execute_single_subtask(st, state, context_str) for st in plan.subtasks]
                await asyncio.gather(*tasks)
            else:
                # Eksekusi sekuensial (misal: Riset dulu -> baru Tulis Esai)
                accumulated_context = context_str
                for st in plan.subtasks:
                    await self._execute_single_subtask(st, state, accumulated_context)
                    # Teruskan output subtask sebelumnya sebagai konteks subtask berikutnya
                    if st.output_data:
                        accumulated_context += f"\nHasil {st.target_agent.value}:\n{str(st.output_data)}"

            # --- TAHAP 3: VERIFY (Audit Kualitas & Verifikasi) ---
            state.status = TaskStatus.VERIFYING
            state.log("Menjalankan Verifier Agent untuk menguji keakuratan dan kelengkapan...")
            verification = await self.verifier.verify(plan.task_goal, state.intermediate_results)
            state.verification = verification

            if verification.is_passed:
                state.log(f"Verifikasi LOLOS dengan skor {verification.score:.2f} ({verification.critique})")
                break
            else:
                state.retry_count += 1
                if state.retry_count <= state.max_retries:
                    state.status = TaskStatus.SELF_CORRECTING
                    state.log(f"Verifikasi GAGAL (Skor {verification.score:.2f}): {verification.critique}. Melakukan Self-Correction...")
                    # Suntikkan saran perbaikan ke subtasks untuk siklus berikutnya
                    for st in plan.subtasks:
                        st.input_data["correction_feedback"] = verification.suggested_fix
                else:
                    state.log(f"Mencapai batas maksimum retry ({state.max_retries}). Mengeluarkan hasil terbaik yang ada.")
                    break

        # --- TAHAP 4: OUTPUT (Sintesis Hasil Akhir) ---
        state.status = TaskStatus.COMPLETED
        state.final_output = self._synthesize_output(state)
        state.log("Tugas selesai. Hasil akhir telah disintesis.")

        # Simpan ke Short-Term Memory & Long-Term Memory
        await self.short_term_memory.store("agent_output", state.final_output[:200], {"session_id": session_id})
        await self.long_term_memory.store(plan.task_goal[:40], state.final_output[:300], {"session_id": session_id})

        return state

    async def _execute_single_subtask(self, subtask: SubTask, state: AgentWorkflowState, context: str):
        agent = self._resolve_agent(subtask.target_agent)
        state.log(f"Agen [{agent.name}] memulai subtask: '{subtask.description}'")
        try:
            output = await agent.execute(subtask.input_data, context=context)
            subtask.output_data = output
            subtask.is_completed = True
            state.intermediate_results[subtask.id] = output
            state.log(f"Agen [{agent.name}] berhasil menyelesaikan subtask '{subtask.id}'.")
        except Exception as e:
            logger.error(f"Error pada subtask {subtask.id} oleh {agent.name}: {e}")
            subtask.error = str(e)
            state.intermediate_results[subtask.id] = {"error": str(e)}

    def _synthesize_output(self, state: AgentWorkflowState) -> str:
        blocks = []
        blocks.append(f"## 🎯 Goal: {state.plan.task_goal if state.plan else state.user_input}\n")

        for subtask in (state.plan.subtasks if state.plan else []):
            data = subtask.output_data or {}
            
            # Format Quiz Output
            if subtask.target_agent == AgentRole.QUIZ and "selected_option" in data:
                blocks.append(f"### 📝 Hasil Analisis Soal Pilihan Ganda")
                blocks.append(f"**Jawaban Terpilih:** `Opsi {data.get('selected_option')}` (Tingkat Keyakinan: {data.get('confidence_score', 1.0)*100:.0f}%)")
                blocks.append(f"\n**Rangkuman Justifikasi:**\n{data.get('summary_justification')}")
                if "options_evaluation" in data:
                    blocks.append("\n**Evaluasi dan Eliminasi Opsi:**")
                    for opt, eval_text in data["options_evaluation"].items():
                        blocks.append(f"- **Opsi {opt}**: {eval_text}")
                if "concept_analysis" in data:
                    blocks.append(f"\n*Analisis Konsep Inti:* {data.get('concept_analysis')}")

            # Format Essay Output
            elif subtask.target_agent == AgentRole.ESSAY and "essay" in data:
                blocks.append(f"### ✍️ Esai Akademis Terstruktur")
                if "outline" in data:
                    blocks.append(f"<details><summary><b>Lihat Kerangka Esai (Outline)</b></summary>\n\n{data.get('outline')}\n\n</details>\n")
                blocks.append(f"{data.get('essay')}")
                blocks.append(f"\n*(Jumlah kata: {data.get('word_count', 0)} kata)*")

            # Format Coding Output
            elif subtask.target_agent == AgentRole.CODING and "code" in data:
                blocks.append(f"### 💻 Solusi Pemrograman & Unit Test")
                lang = data.get("language", "python")
                blocks.append(f"```{lang}\n{data.get('code')}\n```")
                blocks.append(f"\n**Penjelasan Teknis:**\n{data.get('explanation')}")
                if "complexity" in data:
                    comp = data["complexity"]
                    blocks.append(f"- **Time Complexity:** `{comp.get('time', 'N/A')}` | **Space Complexity:** `{comp.get('space', 'N/A')}`")
                if "execution_report" in data and data["execution_report"].get("tested"):
                    rep = data["execution_report"]
                    status_badge = "✅ BERHASIL" if rep["success"] else "❌ GAGAL"
                    blocks.append(f"\n**Hasil Uji Sandbox:** {status_badge}\n```\n{rep.get('output') or rep.get('error')}\n```")

            # Format Research Output
            elif subtask.target_agent == AgentRole.RESEARCH and "key_findings" in data:
                blocks.append(f"### 🔍 Temuan Riset & Fakta Kunci")
                blocks.append(f"{data.get('summary')}\n")
                for item in data.get("key_findings", []):
                    blocks.append(f"- {item}")

        # Tambahkan catatan Verifier di bagian akhir
        if state.verification:
            ver = state.verification
            badge = "✅ Terverifikasi Lolos Mutu" if ver.is_passed else "⚠️ Lolos dengan Catatan"
            blocks.append(f"\n---\n**Quality Assurance Review ({badge} - Skor: {ver.score*100:.0f}%):**\n*{ver.critique}*")

        return "\n\n".join(blocks)
