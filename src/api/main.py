"""FastAPI endpoints for the conversational agent."""

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="mcp-agent-service")


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User message for this turn")
    session_id: str = Field(..., min_length=1, description="Conversation session identifier")


class ChatResponse(BaseModel):
    reply: str


class HealthResponse(BaseModel):
    status: str


def ask(messages: list[dict[str, str]]) -> str:
    """Temporary echo implementation until LLM integration."""
    for message in reversed(messages):
        if message["role"] == "user":
            return message["content"]
    return ""


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.post("/chat", response_model=ChatResponse)
def chat(body: ChatRequest) -> ChatResponse:
    messages = [{"role": "user", "content": body.message}]
    return ChatResponse(reply=ask(messages))
