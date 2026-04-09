# ============================================
# Day 12 Solutions — Inheritance & Polymorphism
# ============================================

from datetime import datetime


# --- Exercise 1: Agent Hierarchy ---
print("--- Agent Hierarchy ---")


class BaseAgent:
    """Base class for all agents."""

    def __init__(self, name: str, model: str = "gpt-4o-mini"):
        self.name = name
        self.model = model
        self.memory: list[dict] = []
        self.call_count = 0

    def think(self, prompt: str) -> str:
        """Process a prompt. Must be overridden by subclasses."""
        raise NotImplementedError("Subclasses must implement think()")

    def remember(self, key: str, value: str):
        self.memory.append({"key": key, "value": value, "time": datetime.now().isoformat()})

    def recall(self, key: str) -> str | None:
        for item in reversed(self.memory):
            if item["key"] == key:
                return item["value"]
        return None

    def __str__(self):
        return f"{self.__class__.__name__}('{self.name}', model='{self.model}')"


class ChatAgent(BaseAgent):
    """Agent for general conversation."""

    def __init__(self, name: str, personality: str = "helpful"):
        super().__init__(name, "gpt-4o-mini")
        self.personality = personality

    def think(self, prompt: str) -> str:
        self.call_count += 1
        return f"[{self.personality}] I'd be happy to help with: {prompt}"


class CodeAgent(BaseAgent):
    """Agent specialized for code generation."""

    SUPPORTED_LANGUAGES = ["python", "javascript", "bash", "yaml"]

    def __init__(self, name: str, language: str = "python"):
        super().__init__(name, "gpt-4o")
        self.language = language

    def think(self, prompt: str) -> str:
        self.call_count += 1
        return f"```{self.language}\n# Generated code for: {prompt}\nprint('Hello from {self.language}!')\n```"

    def set_language(self, lang: str):
        if lang in self.SUPPORTED_LANGUAGES:
            self.language = lang
        else:
            raise ValueError(f"Unsupported language. Choose from: {self.SUPPORTED_LANGUAGES}")


class DevOpsAgent(BaseAgent):
    """Agent specialized for DevOps tasks."""

    def __init__(self, name: str):
        super().__init__(name, "claude-sonnet-4-20250514")
        self.tools = ["docker", "kubectl", "terraform", "ansible"]

    def think(self, prompt: str) -> str:
        self.call_count += 1
        # Route to appropriate tool
        prompt_lower = prompt.lower()
        for tool in self.tools:
            if tool in prompt_lower:
                return f"Using {tool}: Running relevant commands for '{prompt}'"
        return f"DevOps analysis: {prompt}"

    def list_tools(self) -> list[str]:
        return self.tools


# Test polymorphism
agents: list[BaseAgent] = [
    ChatAgent("Chatty", personality="friendly"),
    CodeAgent("Coder", language="python"),
    DevOpsAgent("DevBot"),
]

test_prompt = "Deploy a Docker container with Python app"

print("Polymorphic think():")
for agent in agents:
    result = agent.think(test_prompt)
    print(f"  {agent}")
    print(f"    → {result}\n")


# --- Exercise 2: Provider Abstractions ---
print("--- Provider Abstractions ---")


class LLMProvider:
    """Abstract base class for LLM providers."""

    def __init__(self, name: str, api_key: str = ""):
        self.name = name
        self.api_key = api_key
        self.total_cost = 0.0

    def complete(self, prompt: str, **kwargs) -> str:
        raise NotImplementedError

    def get_models(self) -> list[str]:
        raise NotImplementedError

    def __str__(self):
        return f"{self.__class__.__name__}('{self.name}')"


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str = ""):
        super().__init__("OpenAI", api_key)

    def complete(self, prompt: str, model: str = "gpt-4o-mini", **kwargs) -> str:
        cost = 0.00015 * (len(prompt.split()) / 500)
        self.total_cost += cost
        return f"[OpenAI/{model}] Response to: {prompt[:40]}..."

    def get_models(self) -> list[str]:
        return ["gpt-4o-mini", "gpt-4o"]


class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: str = ""):
        super().__init__("Anthropic", api_key)

    def complete(self, prompt: str, model: str = "claude-haiku-4-20250514", **kwargs) -> str:
        cost = 0.0008 * (len(prompt.split()) / 500)
        self.total_cost += cost
        return f"[Anthropic/{model}] Response to: {prompt[:40]}..."

    def get_models(self) -> list[str]:
        return ["claude-haiku-4-20250514", "claude-sonnet-4-20250514"]


class LocalProvider(LLMProvider):
    def __init__(self):
        super().__init__("Local")

    def complete(self, prompt: str, **kwargs) -> str:
        return f"[Local/llama] Response to: {prompt[:40]}..."

    def get_models(self) -> list[str]:
        return ["llama-3", "mistral-7b", "phi-3"]


# Test
providers: list[LLMProvider] = [
    OpenAIProvider(),
    AnthropicProvider(),
    LocalProvider(),
]

for provider in providers:
    models = provider.get_models()
    result = provider.complete("Explain Kubernetes networking")
    print(f"{provider}")
    print(f"  Models: {models}")
    print(f"  Result: {result}")
    print(f"  Cost: ${provider.total_cost:.4f}\n")


# --- Exercise 3: Event System ---
print("--- Event System ---")


class Event:
    def __init__(self, event_type: str, data: dict):
        self.type = event_type
        self.data = data
        self.timestamp = datetime.now().isoformat()

    def __str__(self):
        return f"Event('{self.type}', {self.data})"


class EventHandler:
    def handle(self, event: Event):
        raise NotImplementedError


class LogHandler(EventHandler):
    def handle(self, event: Event):
        print(f"  📝 LOG: [{event.type}] {event.data}")


class AlertHandler(EventHandler):
    def __init__(self, alert_types: list[str]):
        self.alert_types = alert_types

    def handle(self, event: Event):
        if event.type in self.alert_types:
            print(f"  🚨 ALERT: [{event.type}] {event.data}")


class MetricsHandler(EventHandler):
    def __init__(self):
        self.event_counts: dict[str, int] = {}

    def handle(self, event: Event):
        self.event_counts[event.type] = self.event_counts.get(event.type, 0) + 1

    def report(self):
        print("  📊 Metrics:")
        for event_type, count in self.event_counts.items():
            print(f"    {event_type}: {count}")


class EventBus:
    def __init__(self):
        self.handlers: list[EventHandler] = []

    def subscribe(self, handler: EventHandler):
        self.handlers.append(handler)

    def publish(self, event: Event):
        for handler in self.handlers:
            handler.handle(event)


# Test
bus = EventBus()
metrics = MetricsHandler()

bus.subscribe(LogHandler())
bus.subscribe(AlertHandler(["error", "security"]))
bus.subscribe(metrics)

bus.publish(Event("info", {"message": "Server started"}))
bus.publish(Event("error", {"message": "Database connection failed"}))
bus.publish(Event("security", {"message": "Invalid login attempt", "ip": "10.0.0.1"}))
bus.publish(Event("info", {"message": "Request processed"}))

print()
metrics.report()
