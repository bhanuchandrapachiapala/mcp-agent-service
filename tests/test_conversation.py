"""Tests for in-memory conversation history."""

import sys
from collections.abc import Callable
from pathlib import Path

import pytest

# The project is a src layout and is not installed. Pytest prepends tests/.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.orchestrator.conversation import (
    MAX_CONVERSATION_MESSAGES,
    SYSTEM_PROMPT,
    ConversationOrchestrator,
)

Message = dict[str, str]


def recording_llm() -> tuple[Callable[[list[Message]], str], list[list[Message]]]:
    captured: list[list[Message]] = []

    def llm(messages: list[Message]) -> str:
        captured.append(messages)
        return f"reply-{len(captured)}"

    return llm, captured


@pytest.fixture
def conversation() -> tuple[ConversationOrchestrator, list[list[Message]]]:
    llm, captured = recording_llm()
    return ConversationOrchestrator(llm), captured


def test_first_message_sends_system_prompt_and_returns_reply(conversation):
    orchestrator, captured = conversation

    response = orchestrator.handle_message("session-1", "hello")

    assert response == "reply-1"
    assert captured == [
        [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "hello"},
        ]
    ]


def test_second_message_includes_first_turn(conversation):
    orchestrator, captured = conversation

    orchestrator.handle_message("session-1", "first")
    orchestrator.handle_message("session-1", "second")

    assert captured[1] == [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "first"},
        {"role": "assistant", "content": "reply-1"},
        {"role": "user", "content": "second"},
    ]


def test_sessions_do_not_share_history(conversation):
    orchestrator, captured = conversation

    orchestrator.handle_message("session-a", "alpha")
    orchestrator.handle_message("session-b", "beta")
    orchestrator.handle_message("session-a", "alpha-again")
    orchestrator.handle_message("session-b", "beta-again")

    assert captured[1] == [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "beta"},
    ]
    assert captured[2] == [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "alpha"},
        {"role": "assistant", "content": "reply-1"},
        {"role": "user", "content": "alpha-again"},
    ]
    assert captured[3] == [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "beta"},
        {"role": "assistant", "content": "reply-2"},
        {"role": "user", "content": "beta-again"},
    ]


def test_stored_history_keeps_only_the_most_recent_20_messages(conversation):
    assert MAX_CONVERSATION_MESSAGES == 20
    orchestrator, _captured = conversation

    for turn in range(1, 16):
        orchestrator.handle_message("session-1", f"user-{turn}")

    stored = orchestrator._sessions["session-1"]
    conversation_messages = stored[1:]
    assert len(conversation_messages) == 20

    expected: list[Message] = []
    for turn in range(6, 16):
        expected.append({"role": "user", "content": f"user-{turn}"})
        expected.append({"role": "assistant", "content": f"reply-{turn}"})
    assert conversation_messages == expected


def test_system_prompt_stays_first_after_trimming(conversation):
    orchestrator, captured = conversation
    system_message = {"role": "system", "content": SYSTEM_PROMPT}

    for turn in range(1, 16):
        orchestrator.handle_message("session-1", f"user-{turn}")

    for messages in captured:
        assert messages[0] == system_message
        assert all(message["role"] != "system" for message in messages[1:])

    stored = orchestrator._sessions["session-1"]
    assert stored[0] == system_message
    assert len(stored) == 21
    assert all(message["role"] != "system" for message in stored[1:])
