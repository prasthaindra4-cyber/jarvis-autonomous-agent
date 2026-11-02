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
async def test_conversational_chat_endpoint(monkeypatch):
    async def direct_reply(**kwargs):
        assert "Jawab langsung" in kwargs["system_instruction"]
        return "Jawabannya adalah 42."

    monkeypatch.setattr("app.core.llm_provider.llm_provider.generate", direct_reply)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "message": "Jarvis, berapa jawaban untuk pertanyaan saya?",
            "session_id": "test_voice_session"
        }
        response = await ac.post("/api/v1/agent/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "reply_text" in data
    assert data["is_task"] is False
    assert data["reply_text"] == "Jawabannya adalah 42."

@pytest.mark.asyncio
async def test_conversational_chat_reports_model_failure(monkeypatch):
    async def unavailable(**kwargs):
        raise RuntimeError("Model AI gagal menjawab.")

    monkeypatch.setattr("app.core.llm_provider.llm_provider.generate", unavailable)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/v1/agent/chat", json={
            "message": "Apa kabar?",
            "session_id": "test_voice_failure",
        })

    assert response.status_code == 502
    assert response.json()["detail"] == "Model AI gagal menjawab."

@pytest.mark.asyncio
async def test_screen_analysis_endpoint(monkeypatch):
    async def analyze_image(**kwargs):
        assert kwargs["mime_type"] == "image/jpeg"
        assert kwargs["image_data"] == b"screen"
        return "Jawaban: B, karena penjelasan singkat."

    monkeypatch.setattr("app.core.llm_provider.llm_provider.analyze_image", analyze_image)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/v1/agent/analyze-screen", json={
            "image_base64": "c2NyZWVu",
            "mime_type": "image/jpeg",
            "session_id": "test_screen_session",
        })

    assert response.status_code == 200
    assert response.json()["answer"] == "Jawaban: B, karena penjelasan singkat."

@pytest.mark.asyncio
async def test_screen_analysis_rejects_invalid_base64():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/v1/agent/analyze-screen", json={
            "image_base64": "not base64!",
            "mime_type": "image/jpeg",
        })

    assert response.status_code == 422
