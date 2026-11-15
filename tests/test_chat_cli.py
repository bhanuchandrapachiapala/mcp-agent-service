import json

import httpx
import pytest

from scripts.chat_cli import run_chat, send_message


def test_cli_keeps_same_session_id():
    requests = []

    def mock_api(request):
        requests.append(json.loads(request.content))
        return httpx.Response(200, json={"reply": "Test reply"})

    transport = httpx.MockTransport(mock_api)

    messages = iter(["Hello", "Remember me", "/quit"])
    outputs = []

    with httpx.Client(
        base_url="http://localhost:8000",
        transport=transport,
    ) as client:
        run_chat(
            client,
            session_id="test-session-123",
            read=lambda prompt: next(messages),
            write=outputs.append,
        )

    assert len(requests) == 2
    assert requests[0]["message"] == "Hello"
    assert requests[1]["message"] == "Remember me"

    assert requests[0]["session_id"] == "test-session-123"
    assert requests[1]["session_id"] == "test-session-123"

    assert outputs.count("Bot: Test reply\n") == 2


def test_cli_rejects_invalid_response():
    def mock_api(request):
        return httpx.Response(200, json={"wrong_field": "hello"})

    transport = httpx.MockTransport(mock_api)

    with (
        httpx.Client(
            base_url="http://localhost:8000",
            transport=transport,
        ) as client,
        pytest.raises(TypeError, match="Invalid API response"),
    ):
        send_message(client, "Hello", "test-session")