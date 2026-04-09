# ============================================
# Day 11 Solutions — OOP Basics
# ============================================

from datetime import datetime


# --- Exercise 1: ChatMessage & ChatHistory ---
print("--- ChatMessage & ChatHistory ---")


class ChatMessage:
    """A single chat message."""

    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content
        self.timestamp = datetime.now().isoformat()
        self.token_count = max(1, len(content) // 4)

    def __str__(self):
        return f"[{self.role.upper()}] {self.content[:50]}"

    def __repr__(self):
        return f"ChatMessage(role='{self.role}', tokens={self.token_count})"

    def to_dict(self) -> dict:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp,
            "token_count": self.token_count,
        }


class ChatHistory:
    """Manages a list of ChatMessage objects."""

    def __init__(self, max_messages: int = 100):
        self.messages: list[ChatMessage] = []
        self.max_messages = max_messages

    def add(self, role: str, content: str) -> ChatMessage:
        msg = ChatMessage(role, content)
        self.messages.append(msg)
        # Trim to max
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
        return msg

    def get_last(self, n: int = 5) -> list[ChatMessage]:
        return self.messages[-n:]

    def search(self, keyword: str) -> list[ChatMessage]:
        kw = keyword.lower()
        return [m for m in self.messages if kw in m.content.lower()]

    def total_tokens(self) -> int:
        return sum(m.token_count for m in self.messages)

    def clear(self):
        self.messages.clear()

    def __len__(self):
        return len(self.messages)

    def __str__(self):
        return f"ChatHistory({len(self.messages)} messages, {self.total_tokens()} tokens)"


# Test
history = ChatHistory(max_messages=50)
history.add("user", "How do I deploy a Docker container?")
history.add("assistant", "Use `docker run -d your-image` to deploy a container in detached mode.")
history.add("user", "What about Kubernetes?")
history.add("assistant", "Kubernetes uses `kubectl apply -f deployment.yaml` to deploy workloads.")
history.add("user", "Can you explain Docker networking?")

print(history)
print(f"Total tokens: {history.total_tokens()}")

results = history.search("docker")
print(f"Search 'docker': {len(results)} results")
for msg in results:
    print(f"  {msg}")


# --- Exercise 2: AIModel class ---
print("\n--- AIModel ---")


class AIModel:
    """Tracks an AI model's configuration and usage."""

    def __init__(self, name: str, provider: str, cost_per_1k: float):
        self.name = name
        self.provider = provider
        self.cost_per_1k = cost_per_1k
        self.total_tokens_used = 0
        self.total_requests = 0

    def estimate_cost(self, tokens: int) -> float:
        return (tokens / 1000) * self.cost_per_1k

    def record_usage(self, tokens: int):
        self.total_tokens_used += tokens
        self.total_requests += 1

    def get_total_cost(self) -> float:
        return self.estimate_cost(self.total_tokens_used)

    def __str__(self):
        return f"{self.name} ({self.provider}) — ${self.cost_per_1k}/1K tokens"

    def __repr__(self):
        return f"AIModel('{self.name}', '{self.provider}', {self.cost_per_1k})"

    def compare(self, other: "AIModel", tokens: int) -> str:
        cost_self = self.estimate_cost(tokens)
        cost_other = other.estimate_cost(tokens)
        cheaper = self.name if cost_self < cost_other else other.name
        return (f"For {tokens:,} tokens:\n"
                f"  {self.name}: ${cost_self:.4f}\n"
                f"  {other.name}: ${cost_other:.4f}\n"
                f"  Winner: {cheaper}")


# Test
gpt4 = AIModel("GPT-4o", "OpenAI", 0.005)
gpt_mini = AIModel("GPT-4o-mini", "OpenAI", 0.00015)
claude = AIModel("Claude Sonnet", "Anthropic", 0.003)

print(gpt4)
gpt4.record_usage(5000)
gpt4.record_usage(3000)
print(f"GPT-4o total cost: ${gpt4.get_total_cost():.4f} ({gpt4.total_requests} requests)")

print()
print(gpt4.compare(gpt_mini, 10000))


# --- Exercise 3: ToolRegistry ---
print("\n--- ToolRegistry ---")


class Tool:
    """A callable tool for an AI agent."""

    def __init__(self, name: str, description: str, func):
        self.name = name
        self.description = description
        self.func = func
        self.call_count = 0

    def execute(self, *args, **kwargs):
        self.call_count += 1
        return self.func(*args, **kwargs)

    def __str__(self):
        return f"Tool('{self.name}'): {self.description}"


class ToolRegistry:
    """Registry of tools available to an agent."""

    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, name: str, description: str, func) -> Tool:
        tool = Tool(name, description, func)
        self._tools[name] = tool
        return tool

    def execute(self, name: str, *args, **kwargs):
        if name not in self._tools:
            return f"Error: Tool '{name}' not found. Available: {list(self._tools.keys())}"
        return self._tools[name].execute(*args, **kwargs)

    def list_tools(self) -> list[str]:
        return [f"{t.name}: {t.description}" for t in self._tools.values()]

    def get_stats(self) -> dict:
        return {t.name: t.call_count for t in self._tools.values()}


# Register tools
registry = ToolRegistry()

registry.register("calculator", "Evaluate math expressions", lambda expr: eval(expr))
registry.register("uppercase", "Convert text to uppercase", lambda text: text.upper())
registry.register("word_count", "Count words in text", lambda text: len(text.split()))
registry.register("reverse", "Reverse a string", lambda text: text[::-1])

print("Tools available:")
for tool_info in registry.list_tools():
    print(f"  {tool_info}")

print(f"\ncalculator('2 + 3 * 4') = {registry.execute('calculator', '2 + 3 * 4')}")
print(f"uppercase('hello world') = {registry.execute('uppercase', 'hello world')}")
print(f"word_count('AI agents are cool') = {registry.execute('word_count', 'AI agents are cool')}")
print(f"unknown_tool() = {registry.execute('unknown_tool')}")

print(f"\nTool usage stats: {registry.get_stats()}")
