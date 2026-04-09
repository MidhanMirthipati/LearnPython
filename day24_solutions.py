# ============================================
# Day 24 Solutions — Memory & Context Management
# ============================================

import json
from datetime import datetime
from collections import deque


# --- Exercise 1: Conversation Memory System ---
print("--- Conversation Memory System ---")


class MemoryEntry:
    """A single memory entry."""

    def __init__(self, role: str, content: str, metadata: dict | None = None):
        self.role = role
        self.content = content
        self.timestamp = datetime.now().isoformat()
        self.tokens = max(1, len(content) // 4)
        self.metadata = metadata or {}

    def to_dict(self) -> dict:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp,
            "tokens": self.tokens,
            "metadata": self.metadata,
        }


class SlidingWindowMemory:
    """Fixed-size sliding window over recent messages."""

    def __init__(self, max_messages: int = 20):
        self.max_messages = max_messages
        self.messages: deque[MemoryEntry] = deque(maxlen=max_messages)

    def add(self, role: str, content: str, **metadata):
        self.messages.append(MemoryEntry(role, content, metadata))

    def get_context(self) -> list[dict]:
        return [{"role": m.role, "content": m.content} for m in self.messages]

    def token_count(self) -> int:
        return sum(m.tokens for m in self.messages)

    def __len__(self):
        return len(self.messages)

    def __str__(self):
        return f"SlidingWindow({len(self)}/{self.max_messages} msgs, {self.token_count()} tokens)"


class SummaryMemory:
    """Keeps a running summary + recent messages."""

    def __init__(self, recent_count: int = 5):
        self.summary = ""
        self.recent: deque[MemoryEntry] = deque(maxlen=recent_count)
        self.total_messages = 0

    def add(self, role: str, content: str):
        self.recent.append(MemoryEntry(role, content))
        self.total_messages += 1

        # Update summary when recent buffer is full
        if len(self.recent) == self.recent.maxlen:
            oldest = self.recent[0]
            self.summary += f"\n- [{oldest.role}]: {oldest.content[:50]}"

    def get_context(self) -> list[dict]:
        messages = []
        if self.summary:
            messages.append({
                "role": "system",
                "content": f"Previous conversation summary: {self.summary}"
            })
        messages.extend({"role": m.role, "content": m.content} for m in self.recent)
        return messages


class KeyValueMemory:
    """Persistent key-value store for agent facts."""

    def __init__(self):
        self.store: dict[str, dict] = {}

    def remember(self, key: str, value: str, category: str = "general"):
        self.store[key] = {
            "value": value,
            "category": category,
            "stored_at": datetime.now().isoformat(),
            "access_count": 0,
        }

    def recall(self, key: str) -> str | None:
        if key in self.store:
            self.store[key]["access_count"] += 1
            return self.store[key]["value"]
        return None

    def search(self, query: str) -> list[dict]:
        results = []
        q = query.lower()
        for key, data in self.store.items():
            if q in key.lower() or q in data["value"].lower():
                results.append({"key": key, "value": data["value"]})
        return results

    def get_context_string(self) -> str:
        if not self.store:
            return ""
        lines = ["Known facts:"]
        for key, data in self.store.items():
            lines.append(f"  - {key}: {data['value']}")
        return "\n".join(lines)


# Test
print("Sliding Window:")
window = SlidingWindowMemory(max_messages=5)
for i in range(8):
    window.add("user", f"Message {i}")
    window.add("assistant", f"Reply to message {i}")
print(f"  {window}")
print(f"  Context: {[m['content'] for m in window.get_context()]}\n")

print("Summary Memory:")
summary_mem = SummaryMemory(recent_count=3)
for i in range(6):
    summary_mem.add("user", f"Question about topic {i}")
    summary_mem.add("assistant", f"Answer about topic {i}")
print(f"  Summary: {summary_mem.summary[:100]}")
print(f"  Recent: {[m['content'][:30] for m in summary_mem.recent]}\n")

print("Key-Value Memory:")
kv = KeyValueMemory()
kv.remember("user_name", "Alice", "profile")
kv.remember("preferred_model", "gpt-4o-mini", "settings")
kv.remember("deploy_target", "AWS EKS us-east-1", "infrastructure")
print(f"  user_name: {kv.recall('user_name')}")
print(f"  Search 'gpt': {kv.search('gpt')}")
print(f"  Context: {kv.get_context_string()}")


# --- Exercise 2: Token-Budget Memory ---
print("\n--- Token-Budget Memory ---")


class TokenBudgetMemory:
    """Memory that stays within a token budget."""

    def __init__(self, max_tokens: int = 2000):
        self.max_tokens = max_tokens
        self.system_message: str | None = None
        self.messages: list[MemoryEntry] = []

    def set_system(self, content: str):
        self.system_message = content

    def add(self, role: str, content: str):
        self.messages.append(MemoryEntry(role, content))
        self._trim()

    def _trim(self):
        """Remove oldest messages to stay within budget."""
        while self._total_tokens() > self.max_tokens and len(self.messages) > 2:
            removed = self.messages.pop(0)
            print(f"    ✂️ Trimmed: [{removed.role}] {removed.content[:30]}...")

    def _total_tokens(self) -> int:
        total = 0
        if self.system_message:
            total += len(self.system_message) // 4
        total += sum(m.tokens for m in self.messages)
        return total

    def get_context(self) -> list[dict]:
        result = []
        if self.system_message:
            result.append({"role": "system", "content": self.system_message})
        result.extend({"role": m.role, "content": m.content} for m in self.messages)
        return result

    def __str__(self):
        return f"TokenBudget({self._total_tokens()}/{self.max_tokens} tokens, {len(self.messages)} msgs)"


# Test
budget_mem = TokenBudgetMemory(max_tokens=50)
budget_mem.set_system("You are a helpful assistant.")

messages = [
    "What is Docker?",
    "Docker is a containerization platform for packaging applications.",
    "How does it compare to VMs?",
    "Docker containers share the host OS kernel, making them lighter than VMs.",
    "What about Kubernetes?",
    "Kubernetes orchestrates containers at scale across clusters.",
]

for i, msg in enumerate(messages):
    role = "user" if i % 2 == 0 else "assistant"
    budget_mem.add(role, msg)
    print(f"  After adding: {budget_mem}")


# --- Exercise 3: Hybrid Memory Manager ---
print("\n--- Hybrid Memory Manager ---")


class HybridMemory:
    """Combines sliding window, KV store, and summary."""

    def __init__(self, window_size: int = 10, token_budget: int = 2000):
        self.window = SlidingWindowMemory(window_size)
        self.facts = KeyValueMemory()
        self.summary = ""
        self.token_budget = token_budget

    def add_message(self, role: str, content: str):
        self.window.add(role, content)

        # Auto-extract facts (simple heuristic)
        if "remember" in content.lower() or "my name" in content.lower():
            self.facts.remember(f"fact_{len(self.facts.store)}", content, "auto")

    def add_fact(self, key: str, value: str):
        self.facts.remember(key, value)

    def set_summary(self, summary: str):
        self.summary = summary

    def build_context(self) -> list[dict]:
        context = []

        # 1. System message with facts
        system_parts = ["You are a helpful assistant."]
        facts_str = self.facts.get_context_string()
        if facts_str:
            system_parts.append(facts_str)
        if self.summary:
            system_parts.append(f"\nPrevious conversation: {self.summary}")

        context.append({"role": "system", "content": "\n".join(system_parts)})

        # 2. Recent messages
        context.extend(self.window.get_context())

        return context

    def get_stats(self) -> dict:
        return {
            "recent_messages": len(self.window),
            "stored_facts": len(self.facts.store),
            "has_summary": bool(self.summary),
            "total_tokens": self.window.token_count(),
        }


# Test
hybrid = HybridMemory(window_size=5)
hybrid.add_fact("user_name", "Alice")
hybrid.add_fact("project", "K8s Migration")
hybrid.set_summary("User is learning about container orchestration for a migration project.")

hybrid.add_message("user", "How do I set up an Ingress controller?")
hybrid.add_message("assistant", "You can use nginx-ingress. Install with Helm.")
hybrid.add_message("user", "Remember that we use Istio for service mesh")
hybrid.add_message("assistant", "Noted! I'll keep Istio in mind for your setup.")

context = hybrid.build_context()
print("Built context:")
for msg in context:
    content_preview = msg["content"][:80].replace("\n", " ")
    print(f"  [{msg['role']}] {content_preview}...")

print(f"\nStats: {hybrid.get_stats()}")
