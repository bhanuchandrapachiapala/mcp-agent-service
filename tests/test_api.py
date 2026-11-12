from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_health_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_chat_echoes_message() -> None:
    response = client.post(
        "/chat",
        json={"message": "hello from the client", "session_id": "session-1"},
    )

    assert response.status_code == 200
    assert response.json() == {"reply": "hello from the client"}


def test_chat_echoes_each_message_independently() -> None:
    first = client.post(
        "/chat",
        json={"message": "first", "session_id": "session-a"},
    )
    second = client.post(
        "/chat",
        json={"message": "second", "session_id": "session-b"},
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json() == {"reply": "first"}
    assert second.json() == {"reply": "second"}


def test_chat_sends_message_list_to_ask(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_ask(messages: list[dict[str, str]]) -> str:
        captured["messages"] = messages
        return "stub-reply"

    monkeypatch.setattr("src.api.main.ask", fake_ask)

    response = client.post(
        "/chat",
        json={"message": "hi", "session_id": "session-1"},
    )

    assert response.status_code == 200
    assert response.json() == {"reply": "stub-reply"}
    assert captured["messages"] == [{"role": "user", "content": "hi"}]


def test_chat_rejects_empty_fields() -> None:
    empty_message = client.post(
        "/chat",
        json={"message": "", "session_id": "session-1"},
    )
    empty_session = client.post(
        "/chat",
        json={"message": "hello", "session_id": ""},
    )

    assert empty_message.status_code == 422
    assert empty_session.status_code == 422


def test_chat_requires_message_and_session_id() -> None:
    missing_message = client.post("/chat", json={"session_id": "session-1"})
    missing_session = client.post("/chat", json={"message": "hello"})
    empty_body = client.post("/chat", json={})

    assert missing_message.status_code == 422
    assert missing_session.status_code == 422
    assert empty_body.status_code == 422
