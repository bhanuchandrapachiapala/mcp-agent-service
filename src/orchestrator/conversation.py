"""In-memory conversation history keyed by session."""

from collections.abc import Callable

SYSTEM_PROMPT = "You are a helpful assistant."
MAX_CONVERSATION_MESSAGES = 20

Message = dict[str, str]
LLM = Callable[[list[Message]], str]


class ConversationOrchestrator:
    """Handle one user message at a time and remember each session.

    Sessions are stored in a dictionary of message lists. Every list starts
    with a system prompt, which is kept when older turns are dropped. Only the
    most recent user and assistant messages are retained.
    """

    def __init__(self, llm: LLM) -> None:
        self._llm = llm
        self._sessions: dict[str, list[Message]] = {}

    def handle_message(self, session_id: str, content: str) -> str:
        """Store the user message, call the LLM with full history, and store the reply.

        The callable receives the system prompt, prior turns from this session,
        and the new user message. It returns the assistant response text.
        """
        history = self._history(session_id)
        history.append({"role": "user", "content": content})
        self._trim(history)

        response = self._llm([message.copy() for message in history])

        history.append({"role": "assistant", "content": response})
        self._trim(history)
        return response

    def _history(self, session_id: str) -> list[Message]:
        history = self._sessions.get(session_id)
        if history is None:
            history = [{"role": "system", "content": SYSTEM_PROMPT}]
            self._sessions[session_id] = history
        return history

    def _trim(self, history: list[Message]) -> None:
        excess = len(history) - 1 - MAX_CONVERSATION_MESSAGES
        if excess > 0:
            del history[1 : 1 + excess]
