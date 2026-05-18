"""Per-user short-term conversation memory.

Trivial in-process implementation: a deque per user_id, trimmed by a rough
character budget. Good enough for a single-instance bot; swap for Redis or
SQLite if/when we scale out.
"""

from __future__ import annotations

from collections import defaultdict, deque

from .llm import ChatMessage


class ConversationMemory:
    def __init__(self, char_budget: int = 8000) -> None:
        self._budget = char_budget
        self._store: dict[int, deque[ChatMessage]] = defaultdict(deque)

    def append(self, user_id: int, message: ChatMessage) -> None:
        self._store[user_id].append(message)
        self._trim(user_id)

    def history(self, user_id: int) -> list[ChatMessage]:
        return list(self._store[user_id])

    def reset(self, user_id: int) -> None:
        self._store.pop(user_id, None)

    def _trim(self, user_id: int) -> None:
        dq = self._store[user_id]
        total = sum(len(m.content) for m in dq)
        while total > self._budget and len(dq) > 1:
            removed = dq.popleft()
            total -= len(removed.content)
