import httpx
import ollama
import pytest

from src.llm import client
from src.llm.client import LLMError, ask


class FakeClient:
    """Stands in for ollama.Client; returns a canned reply or raises a preset error."""

    reply = "hi there"
    error = None

    def __init__(self, host=None):
        self.host = host

    def chat(self, model, messages):
        if self.error:
            raise self.error
        return {"message": {"role": "assistant", "content": self.reply}}


@pytest.fixture
def fake_client(monkeypatch):
    FakeClient.error = None
    monkeypatch.setattr(client.ollama, "Client", FakeClient)
    return FakeClient


def test_ask_returns_reply_text(fake_client):
    assert ask([{"role": "user", "content": "hello"}]) == "hi there"


def test_ask_ollama_not_running(fake_client):
    fake_client.error = ConnectionError("connection refused")
    with pytest.raises(LLMError, match="ollama serve"):
        ask([{"role": "user", "content": "hello"}])


def test_ask_server_drops_connection(fake_client):
    fake_client.error = httpx.RemoteProtocolError("Server disconnected without sending a response.")
    with pytest.raises(LLMError, match="ollama run"):
        ask([{"role": "user", "content": "hello"}])


def test_ask_model_missing(fake_client):
    fake_client.error = ollama.ResponseError("model not found", status_code=404)
    with pytest.raises(LLMError, match="ollama pull"):
        ask([{"role": "user", "content": "hello"}])
