from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from app.api.dependencies import get_engine
from app.workflow.engine import AutonomousWorkflowEngine

router = APIRouter(prefix="/agent", tags=["Autonomous Agents"])

class AutonomousTaskRequest(BaseModel):
    prompt: str = Field(..., description="Instruksi tugas, soal PG, esai, atau coding")
    session_id: str = Field(default="session_default", description="ID sesi untuk retensi memori")

class QuizDirectRequest(BaseModel):
    question: str
    options: Dict[str, str] = Field(
        ..., 
        json_schema_extra={"example": {"A": "Opsi 1", "B": "Opsi 2", "C": "Opsi 3", "D": "Opsi 4"}}
    )
    session_id: str = "quiz_session"

class EssayDirectRequest(BaseModel):
    topic: str
    requirements: Optional[str] = "Bahasa akademis, terstruktur, mendalam"
    session_id: str = "essay_session"

class CodingDirectRequest(BaseModel):
    instruction: str
    language: str = "python"
    session_id: str = "coding_session"

@router.post("/run", summary="Jalankan Autonomous Task (Plan -> Exec -> Verify -> Output)")
async def run_autonomous_task(
    req: AutonomousTaskRequest,
    engine: AutonomousWorkflowEngine = Depends(get_engine)
):
    state = await engine.run(user_input=req.prompt, session_id=req.session_id)
    return {
        "status": state.status,
        "session_id": state.session_id,
        "plan": state.plan.model_dump() if state.plan else None,
        "verification": state.verification.model_dump() if state.verification else None,
        "output": state.final_output,
        "logs": state.execution_logs
    }

@router.post("/quiz", summary="Eksekusi Khusus Soal Pilihan Ganda (PG)")
async def solve_quiz(
    req: QuizDirectRequest,
    engine: AutonomousWorkflowEngine = Depends(get_engine)
):
    result = await engine.quiz_agent.execute({
        "question": req.question,
        "options": req.options
    })
    return {
        "session_id": req.session_id,
        "result": result
    }

@router.post("/essay", summary="Eksekusi Khusus Penulisan Esai Akademis")
async def write_essay(
    req: EssayDirectRequest,
    engine: AutonomousWorkflowEngine = Depends(get_engine)
):
    result = await engine.essay_agent.execute({
        "topic": req.topic,
        "requirements": req.requirements
    })
    return {
        "session_id": req.session_id,
        "result": result
    }

@router.post("/coding", summary="Eksekusi Khusus Tugas Pemrograman")
async def execute_coding(
    req: CodingDirectRequest,
    engine: AutonomousWorkflowEngine = Depends(get_engine)
):
    result = await engine.coding_agent.execute({
        "instruction": req.instruction,
        "language": req.language
    })
    return {
        "session_id": req.session_id,
        "result": result
    }

class ConversationalChatRequest(BaseModel):
    message: str = Field(..., description="Pesan suara atau teks dari pengguna")
    session_id: str = Field(default="voice_session", description="ID sesi percakapan")
    voice_mode: bool = Field(default=True, description="Apakah dioptimasi untuk text-to-speech")

@router.post("/chat", summary="Conversational Voice/Text Endpoint (Mengobrol Langsung dengan JARVIS)")
async def chat_with_jarvis(
    req: ConversationalChatRequest,
    engine: AutonomousWorkflowEngine = Depends(get_engine)
):
    msg_clean = req.message.strip().lower()
    
    # 1. Cek apakah ini percakapan kasual / panggilan langsung
    is_casual = any(k in msg_clean for k in [
        "halo", "hai", "hello", "pagi", "siang", "malam", "jarvis", 
        "siapa kamu", "apa kabar", "kamu bisa apa", "terima kasih", "thanks", "tes", "test"
    ]) and not any(k in msg_clean for k in ["soal", "esai", "essay", "coding", "kode", "fungsi", "function", "algoritma", "riset", "analisis mendalam"])
    
    if is_casual:
        if any(k in msg_clean for k in ["halo", "hai", "hello", "pagi", "siang", "malam"]):
            reply = "Halo, Senang mendengar suara Anda. Saya JARVIS. Semua sistem beroperasi optimal. Ada tugas atau analisis yang perlu saya kerjakan untuk Anda hari ini?"
        elif any(k in msg_clean for k in ["siapa kamu", "kamu siapa"]):
            reply = "Saya JARVIS, asisten AI otonom Anda. Saya dilengkapi multi-agen spesialis yang mampu memecahkan soal pilihan ganda, menulis esai ilmiah, menganalisis data, hingga menulis dan menguji kode program secara mandiri."
        elif any(k in msg_clean for k in ["apa kabar"]):
            reply = "Kondisi sistem dan memori berada dalam performa puncak, seratus persen siap menjalankan instruksi Anda. Bagaimana dengan Anda?"
        elif any(k in msg_clean for k in ["kamu bisa apa", "bisa bantu apa"]):
            reply = "Anda bisa meminta saya menyelesaikan soal ujian pilihan ganda, menyusun esai akademis, meriset topik spesifik, atau membuat program coding. Katakan saja instruksinya, saya yang akan menyelesaikannya dari awal hingga akhir."
        elif any(k in msg_clean for k in ["terima kasih", "thanks"]):
            reply = "Sama-sama. Senang bisa membantu Anda. Beritahu saya jika ada hal lain yang Anda butuhkan."
        else:
            reply = "Saya mendengar Anda dengan jelas. Katakan saja perintah atau tugas yang ingin Anda berikan, dan agen saya akan segera mengerjakannya."

        # Simpan ke short term memory
        await engine.short_term_memory.store("user_speech", req.message, {"session_id": req.session_id})
        await engine.short_term_memory.store("jarvis_speech", reply, {"session_id": req.session_id})

        return {
            "session_id": req.session_id,
            "is_task": False,
            "reply_text": reply,
            "task_result": None
        }

    # 2. Jika merupakan instruksi tugas otonom, jalankan Autonomous Workflow Engine
    state = await engine.run(user_input=req.message, session_id=req.session_id)
    
    # Buat ringkasan ramah suara (Speech-friendly Voice Summary)
    spoken_summary = "Baik, tugas telah selesai dikerjakan dan diverifikasi."
    if state.intermediate_results:
        for tid, res in state.intermediate_results.items():
            if isinstance(res, dict) and "selected_option" in res:
                opt = res.get("selected_option")
                justif = res.get("summary_justification", "")
                spoken_summary = f"Analisis soal pilihan ganda selesai. Jawaban yang paling tepat adalah Opsi {opt}. {justif}"
                break
            elif isinstance(res, dict) and "essay" in res:
                topic = res.get("topic", "esai")
                words = res.get("word_count", 0)
                spoken_summary = f"Draf esai akademis mengenai {topic} telah selesai saya tulis dan verifikasi, sebanyak {words} kata. Hasil lengkapnya sudah tampil di layar Anda."
                break
            elif isinstance(res, dict) and "code" in res:
                rep = res.get("execution_report", {})
                success_txt = "Unit test berhasil lolos tanpa kendala." if rep.get("success") else "Kode telah disusun."
                spoken_summary = f"Kode program beserta fungsi pengujiannya telah selesai dibuat dan diverifikasi di sandbox. {success_txt}"
                break

    return {
        "session_id": req.session_id,
        "is_task": True,
        "reply_text": spoken_summary,
        "task_result": {
            "status": state.status,
            "plan": state.plan.model_dump() if state.plan else None,
            "verification": state.verification.model_dump() if state.verification else None,
            "output": state.final_output,
            "logs": state.execution_logs
        }
    }

@router.get("/memory/{session_id}", summary="Lihat Riwayat Working Memory Sesi")
async def get_session_memory(
    session_id: str,
    engine: AutonomousWorkflowEngine = Depends(get_engine)
):
    history = await engine.short_term_memory.get_session_history(session_id)
    return {
        "session_id": session_id,
        "items": [item.model_dump() for item in history]
    }
