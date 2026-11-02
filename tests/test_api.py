import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

@pytest.mark.asyncio
async def test_api_run_quiz_task():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "prompt": "Soal PG: Apa fungsi utama RAM? A. Penyimpanan permanen B. Memori volatil berkecepatan tinggi",
            "session_id": "test_api_session"
        }
        response = await ac.post("/api/v1/agent/run", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert "output" in data
    assert data["plan"] is not None

@pytest.mark.asyncio
async def test_direct_quiz_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "question": "Berapakah hasil 2 + 2?",
            "options": {"A": "3", "B": "4", "C": "5"}
        }
        response = await ac.post("/api/v1/agent/quiz", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert "selected_option" in data["result"]

@pytest.mark.asyncio
async def test_conversational_chat_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "message": "Halo Jarvis, apa kabar?",
            "session_id": "test_voice_session"
        }
        response = await ac.post("/api/v1/agent/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "reply_text" in data
    assert data["is_task"] is False
    assert len(data["reply_text"]) > 10
