import pytest
from app.workflow.engine import AutonomousWorkflowEngine
from app.workflow.state import TaskStatus

@pytest.mark.asyncio
async def test_full_autonomous_quiz_workflow():
    engine = AutonomousWorkflowEngine()
    prompt = "Soal Pilihan Ganda: Manakah komponen utama CPU? A. ALU B. Ban C. Kursi D. Monitor"
    state = await engine.run(user_input=prompt, session_id="test_quiz_session")

    assert state.status == TaskStatus.COMPLETED
    assert state.plan is not None
    assert state.final_output is not None
    assert "Jawaban Terpilih" in state.final_output or "Hasil Analisis" in state.final_output
    assert state.verification is not None
    assert state.verification.is_passed is True

@pytest.mark.asyncio
async def test_full_autonomous_essay_workflow():
    engine = AutonomousWorkflowEngine()
    prompt = "Buatkan esai komprehensif mengenai etika AI"
    state = await engine.run(user_input=prompt, session_id="test_essay_session")

    assert state.status == TaskStatus.COMPLETED
    assert state.final_output is not None
    assert len(state.final_output) > 100

@pytest.mark.asyncio
async def test_memory_layer():
    engine = AutonomousWorkflowEngine()
    session_id = "mem_test_session"
    
    # Simpan di short term memory
    await engine.short_term_memory.store("context_1", "User adalah seorang software architect", {"session_id": session_id})
    history = await engine.short_term_memory.get_session_history(session_id)
    assert len(history) >= 1
    assert "software architect" in history[0].content

    # Simpan di long term memory
    await engine.long_term_memory.store("tech_stack", "Tech stack yang dipakai adalah FastAPI dan Gemini", {"session_id": session_id})
    retrieved = await engine.long_term_memory.retrieve("FastAPI")
    assert len(retrieved) >= 1
    assert "Gemini" in retrieved[0].content
