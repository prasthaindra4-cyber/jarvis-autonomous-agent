import pytest
from app.agents.coordinator import CoordinatorAgent
from app.agents.quiz_agent import QuizAgent
from app.agents.essay_agent import EssayAgent
from app.agents.coding_agent import CodingAgent
from app.agents.research_agent import ResearchAgent
from app.workflow.verifier import VerifierAgent

@pytest.mark.asyncio
async def test_coordinator_agent():
    coordinator = CoordinatorAgent()
    plan = await coordinator.decompose_and_route("Soal Pilihan Ganda: Apa kepanjangan dari ACID?")
    assert plan is not None
    assert len(plan.subtasks) >= 1
    assert plan.subtasks[0].target_agent.value in ["quiz", "research"]

@pytest.mark.asyncio
async def test_quiz_agent():
    quiz_agent = QuizAgent()
    payload = {
        "question": "Apa itu konsistensi dalam ACID?",
        "options": {
            "A": "Sistem selalu cepat",
            "B": "Menjaga database tetap valid sesuai aturan dan constraint"
        }
    }
    result = await quiz_agent.execute(payload)
    assert "selected_option" in result
    assert "summary_justification" in result
    assert "options_evaluation" in result

@pytest.mark.asyncio
async def test_essay_agent():
    essay_agent = EssayAgent()
    payload = {
        "topic": "Transformasi Kecerdasan Buatan dalam Industri",
        "requirements": "Bahasa akademis dan formal"
    }
    result = await essay_agent.execute(payload)
    assert "essay" in result
    assert "outline" in result
    assert result["word_count"] > 20

@pytest.mark.asyncio
async def test_coding_agent_and_sandbox():
    coding_agent = CodingAgent()
    payload = {
        "instruction": "Tulis fungsi fibonacci(n) dan unit test-nya",
        "language": "python"
    }
    result = await coding_agent.execute(payload)
    assert "code" in result
    assert "language" in result
    assert result["language"] == "python"
    assert "execution_report" in result

@pytest.mark.asyncio
async def test_verifier_agent():
    verifier = VerifierAgent()
    verif = await verifier.verify(
        original_goal="Menyelesaikan soal pilihan ganda",
        intermediate_results={
            "selected_option": "B",
            "summary_justification": "Sesuai teori"
        }
    )
    assert verif.is_passed is True
    assert verif.score >= 0.8
