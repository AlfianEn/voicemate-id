"""Smoke tests for ConversationMemory."""

from voicemate.llm import ChatMessage
from voicemate.memory import ConversationMemory


def test_append_and_history() -> None:
    mem = ConversationMemory(char_budget=1000)
    mem.append(1, ChatMessage(role="user", content="halo"))
    mem.append(1, ChatMessage(role="assistant", content="hai"))

    history = mem.history(1)
    assert [m.role for m in history] == ["user", "assistant"]
    assert [m.content for m in history] == ["halo", "hai"]


def test_isolation_between_users() -> None:
    mem = ConversationMemory()
    mem.append(1, ChatMessage(role="user", content="A"))
    mem.append(2, ChatMessage(role="user", content="B"))

    assert [m.content for m in mem.history(1)] == ["A"]
    assert [m.content for m in mem.history(2)] == ["B"]


def test_trim_respects_budget() -> None:
    mem = ConversationMemory(char_budget=10)
    for _i in range(5):
        mem.append(1, ChatMessage(role="user", content="abcdef"))  # 6 chars each

    history = mem.history(1)
    total = sum(len(m.content) for m in history)
    assert total <= 10
    # at least one message survives even if the budget is tiny
    assert len(history) >= 1


def test_reset() -> None:
    mem = ConversationMemory()
    mem.append(1, ChatMessage(role="user", content="halo"))
    mem.reset(1)
    assert mem.history(1) == []
