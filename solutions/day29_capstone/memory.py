# ============================================
# Capstone Project — DevOps Assistant Agent
# Memory Module
# ============================================

from collections import deque
from datetime import datetime


class MemoryEntry:
    """A single memory entry (message or fact)."""

    def __init__(self, role: str, content: str, metadata: dict | None = None):
        self.role = role
        self.content = content
        self.timestamp = datetime.now().isoformat()
        self.tokens = max(1, len(content) // 4)
        self.metadata = metadata or {}

    def to_api_format(self) -> dict:
        return {"role": self.role, "content": self.content}

    def __str__(self):
        return f"[{self.role}] {self.content[:50]}"


class ConversationMemory:
    """Manages conversation history with a sliding window and token budget."""

    def __init__(self, max_messages: int = 20, token_budget: int = 4000):
        self.max_messages = max_messages
        self.token_budget = token_budget
        self.messages: deque[MemoryEntry] = deque(maxlen=max_messages)
        self.facts: dict[str, str] = {}
        self.summary: str = ""
        self.total_messages_processed = 0

    def add_message(self, role: str, content: str, **metadata) -> MemoryEntry:
        """Add a message to conversation history."""
        entry = MemoryEntry(role, content, metadata)
        self.messages.append(entry)
        self.total_messages_processed += 1
        self._enforce_budget()
        return entry

    def add_fact(self, key: str, value: str):
        """Store a persistent fact."""
        self.facts[key] = value

    def recall_fact(self, key: str) -> str | None:
        """Retrieve a stored fact."""
        return self.facts.get(key)

    def search_facts(self, query: str) -> list[dict]:
        """Search facts by keyword."""
        q = query.lower()
        return [
            {"key": k, "value": v}
            for k, v in self.facts.items()
            if q in k.lower() or q in v.lower()
        ]

    def _enforce_budget(self):
        """Remove oldest messages to stay within token budget."""
        while self._current_tokens() > self.token_budget and len(self.messages) > 2:
            self.messages.popleft()

    def _current_tokens(self) -> int:
        """Calculate current token usage."""
        total = 0
        if self.summary:
            total += len(self.summary) // 4
        total += sum(len(f"{k}: {v}") // 4 for k, v in self.facts.items())
        total += sum(m.tokens for m in self.messages)
        return total

    def build_context(self, system_prompt: str) -> list[dict]:
        """Build the full context for an API call."""
        context = []

        # System prompt with facts and summary
        system_parts = [system_prompt]

        if self.facts:
            facts_str = "\n".join(f"- {k}: {v}" for k, v in self.facts.items())
            system_parts.append(f"\nKnown facts:\n{facts_str}")

        if self.summary:
            system_parts.append(f"\nConversation summary:\n{self.summary}")

        context.append({"role": "system", "content": "\n".join(system_parts)})

        # Recent messages
        for msg in self.messages:
            context.append(msg.to_api_format())

        return context

    def get_stats(self) -> dict:
        return {
            "current_messages": len(self.messages),
            "max_messages": self.max_messages,
            "stored_facts": len(self.facts),
            "current_tokens": self._current_tokens(),
            "token_budget": self.token_budget,
            "total_processed": self.total_messages_processed,
        }

    def clear(self):
        """Clear conversation but keep facts."""
        self.messages.clear()
        self.summary = ""

    def clear_all(self):
        """Clear everything including facts."""
        self.clear()
        self.facts.clear()
