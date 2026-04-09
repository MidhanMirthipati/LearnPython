# Day 24: Memory & State Management for Agents

## Learning Goals
- Understand different types of agent memory
- Implement conversation windowing and summarization
- Build short-term and long-term memory systems
- Manage token budgets with memory

---

## 1. Types of Agent Memory

| Type | Description | Example |
|------|-------------|---------|
| **Conversation** | The chat history | Messages list |
| **Short-term** | Current task context | Variables, scratchpad |
| **Long-term** | Persistent facts | User preferences, saved data |
| **Episodic** | Past experience | Previous conversation summaries |
| **Semantic** | Factual knowledge | Vector database / RAG |

---

## 2. Conversation Memory (Window Strategy)

The simplest approach: keep the last N messages.

```python
class WindowMemory:
    """Keep only the last N messages (plus system prompt)."""
    
    def __init__(self, system_prompt: str, window_size: int = 10):
        self.system_prompt = system_prompt
        self.window_size = window_size
        self.all_messages: list[dict] = []
    
    def add(self, role: str, content: str):
        self.all_messages.append({"role": role, "content": content})
    
    def get_messages(self) -> list[dict]:
        """Return system prompt + last N messages."""
        system = [{"role": "system", "content": self.system_prompt}]
        window = self.all_messages[-self.window_size:]
        return system + window
    
    def total_messages(self) -> int:
        return len(self.all_messages)

# Usage
memory = WindowMemory("You are a DevOps assistant.", window_size=6)
for i in range(20):
    memory.add("user", f"Message {i}")
    memory.add("assistant", f"Response {i}")

context = memory.get_messages()
print(f"Total messages: {memory.total_messages()}")  # 40
print(f"In context: {len(context)}")  # 7 (1 system + 6 windowed)
```

---

## 3. Summary Memory

Summarize older messages to compress context:

```python
from openai import OpenAI  # Using OpenAI here; see Day 17 for Anthropic/Gemini equivalents
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

class SummaryMemory:
    """Summarize old messages, keep recent ones in full."""
    
    def __init__(self, system_prompt: str, keep_recent: int = 6, max_before_summarize: int = 12):
        self.system_prompt = system_prompt
        self.keep_recent = keep_recent
        self.max_before_summarize = max_before_summarize
        self.messages: list[dict] = []
        self.summary: str = ""
    
    def add(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
        
        if len(self.messages) >= self.max_before_summarize:
            self._summarize_old()
    
    def _summarize_old(self):
        """Summarize old messages and keep only recent ones."""
        old_messages = self.messages[:-self.keep_recent]
        
        summary_prompt = "Summarize this conversation concisely, preserving key facts and decisions:\n\n"
        for msg in old_messages:
            summary_prompt += f"{msg['role'].upper()}: {msg['content']}\n"
        
        if self.summary:
            summary_prompt = f"Previous summary: {self.summary}\n\nNew messages to incorporate:\n" + summary_prompt
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Summarize conversations concisely. Keep key facts, decisions, and action items."},
                {"role": "user", "content": summary_prompt}
            ],
            max_tokens=200,
            temperature=0
        )
        
        self.summary = response.choices[0].message.content
        self.messages = self.messages[-self.keep_recent:]
        print(f"[Memory] Summarized. Summary: {self.summary[:80]}...")
    
    def get_messages(self) -> list[dict]:
        """Return system prompt + summary + recent messages."""
        result = [{"role": "system", "content": self.system_prompt}]
        
        if self.summary:
            result.append({
                "role": "system",
                "content": f"Summary of earlier conversation: {self.summary}"
            })
        
        result.extend(self.messages)
        return result
```

---

## 4. Long-Term Memory (Key-Value Store)

```python
import json
from pathlib import Path
from datetime import datetime

class LongTermMemory:
    """Persistent key-value memory stored on disk."""
    
    def __init__(self, filepath: str = "agent_memory.json"):
        self.filepath = Path(filepath)
        self.memories: dict[str, dict] = {}
        self._load()
    
    def _load(self):
        if self.filepath.exists():
            with open(self.filepath) as f:
                self.memories = json.load(f)
    
    def _save(self):
        with open(self.filepath, "w") as f:
            json.dump(self.memories, f, indent=2)
    
    def store(self, key: str, value: str, category: str = "general"):
        self.memories[key] = {
            "value": value,
            "category": category,
            "stored_at": datetime.now().isoformat(),
            "access_count": 0
        }
        self._save()
    
    def recall(self, key: str) -> str | None:
        if key in self.memories:
            self.memories[key]["access_count"] += 1
            self._save()
            return self.memories[key]["value"]
        return None
    
    def search(self, query: str) -> list[dict]:
        """Search memories by keyword."""
        results = []
        query_lower = query.lower()
        for key, data in self.memories.items():
            if query_lower in key.lower() or query_lower in data["value"].lower():
                results.append({"key": key, **data})
        return results
    
    def get_by_category(self, category: str) -> dict:
        return {
            k: v for k, v in self.memories.items()
            if v["category"] == category
        }
    
    def forget(self, key: str):
        if key in self.memories:
            del self.memories[key]
            self._save()
    
    def get_context_string(self, max_items: int = 10) -> str:
        """Generate a context string for LLM injection."""
        if not self.memories:
            return "No stored memories."
        
        # Sort by most recently accessed
        sorted_memories = sorted(
            self.memories.items(),
            key=lambda x: x[1].get("stored_at", ""),
            reverse=True
        )[:max_items]
        
        lines = ["Known facts about the user/environment:"]
        for key, data in sorted_memories:
            lines.append(f"- {key}: {data['value']}")
        
        return "\n".join(lines)

# Usage
memory = LongTermMemory("my_agent_memory.json")
memory.store("user_name", "Alice", category="user")
memory.store("preferred_model", "gpt-4o-mini", category="preferences")
memory.store("server_ip", "192.168.1.100", category="infrastructure")
memory.store("k8s_cluster", "prod-us-east-1", category="infrastructure")

print(memory.recall("user_name"))  # "Alice"
print(memory.search("server"))     # Finds server_ip
print(memory.get_by_category("infrastructure"))
print(memory.get_context_string())
```

---

## 5. Scratchpad Memory (Working Memory)

```python
class Scratchpad:
    """Working memory for multi-step tasks."""
    
    def __init__(self):
        self.notes: list[str] = []
        self.plan: list[dict] = []
        self.findings: dict[str, str] = {}
    
    def add_note(self, note: str):
        self.notes.append(note)
    
    def set_plan(self, steps: list[str]):
        self.plan = [{"step": s, "status": "pending"} for s in steps]
    
    def complete_step(self, step_index: int, result: str):
        if step_index < len(self.plan):
            self.plan[step_index]["status"] = "done"
            self.plan[step_index]["result"] = result
    
    def add_finding(self, key: str, value: str):
        self.findings[key] = value
    
    def get_context(self) -> str:
        """Generate context string for LLM."""
        parts = []
        
        if self.plan:
            parts.append("Current plan:")
            for i, step in enumerate(self.plan):
                status = "✅" if step["status"] == "done" else "⬜"
                parts.append(f"  {status} {i+1}. {step['step']}")
                if "result" in step:
                    parts.append(f"       Result: {step['result'][:50]}")
        
        if self.findings:
            parts.append("\nFindings:")
            for k, v in self.findings.items():
                parts.append(f"  - {k}: {v}")
        
        if self.notes:
            parts.append("\nNotes:")
            for note in self.notes[-5:]:
                parts.append(f"  - {note}")
        
        return "\n".join(parts) if parts else "No working context."
```

---

## 6. Complete Agent with Memory

```python
class MemoryAgent:
    """Agent with full memory capabilities."""
    
    def __init__(self, name: str, system_prompt: str):
        self.name = name
        self.conversation = SummaryMemory(system_prompt)
        self.long_term = LongTermMemory(f"{name}_memory.json")
        self.scratchpad = Scratchpad()
    
    def _build_context(self) -> list[dict]:
        """Build full context with all memory types."""
        messages = self.conversation.get_messages()
        
        # Inject long-term memory
        lt_context = self.long_term.get_context_string()
        if lt_context != "No stored memories.":
            messages.insert(1, {
                "role": "system",
                "content": f"Long-term memory:\n{lt_context}"
            })
        
        # Inject scratchpad
        sp_context = self.scratchpad.get_context()
        if sp_context != "No working context.":
            messages.insert(2, {
                "role": "system",
                "content": f"Working memory:\n{sp_context}"
            })
        
        return messages
    
    def chat(self, user_message: str) -> str:
        self.conversation.add("user", user_message)
        
        messages = self._build_context()
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7
        )
        
        answer = response.choices[0].message.content
        self.conversation.add("assistant", answer)
        
        return answer
```

---

## 7. Exercises

### Exercise 1: Token-Aware Memory
```python
# Build a memory system that:
# 1. Tracks token count of each message
# 2. Has a token budget (e.g., 4000 tokens)
# 3. Removes oldest messages when budget is exceeded
# 4. Prioritizes keeping system prompt and recent messages
# 5. Reports: "Using X/4000 tokens in context"
```

### Exercise 2: Semantic Memory Search
```python
# Build a memory that stores facts with keyword tags:
# memory.store("Docker port mapping", tags=["docker", "networking"])
# memory.search_by_tags(["docker"]) → returns all docker-tagged memories
# memory.get_relevant(user_query) → uses keyword matching to find relevant memories
```

### Exercise 3: Episodic Memory
```python
# Build an episodic memory that:
# 1. Saves complete conversation summaries when a session ends
# 2. Loads relevant past summaries when starting a new session
# 3. Uses keyword matching to find relevant past episodes
# 4. Injects relevant episodes into the system prompt
```

---

## Solutions

See [solutions/day24_solutions.py](../solutions/day24_solutions.py)

---

## Key Takeaways
- Window memory: Simple, keep last N messages
- Summary memory: Compress old messages into summaries
- Long-term memory: Persistent key-value store on disk
- Scratchpad: Working memory for multi-step plans
- Inject memory context into system messages
- Always manage token budgets — context windows have limits

**Tomorrow:** Building agents with LangChain →
