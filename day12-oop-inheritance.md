# Day 12: OOP — Inheritance & Composition

## Learning Goals
- Use inheritance to create specialized classes
- Understand method overriding and `super()`
- Choose between inheritance and composition
- Build an agent hierarchy

---

## 1. Inheritance Basics

```python
class BaseAgent:
    """Base class for all agents."""
    
    def __init__(self, name: str, model: str = "gpt-3.5-turbo"):
        self.name = name
        self.model = model
        self.messages: list[dict] = []
    
    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
    
    def respond(self, user_input: str) -> str:
        """Default response method."""
        self.add_message("user", user_input)
        response = f"I received: {user_input}"
        self.add_message("assistant", response)
        return response
    
    def __str__(self):
        return f"{self.__class__.__name__}('{self.name}')"


class DevOpsAgent(BaseAgent):
    """Specialized agent for DevOps tasks."""
    
    def __init__(self, name: str, specialties: list[str] | None = None):
        super().__init__(name, model="gpt-4")  # Call parent __init__
        self.specialties = specialties or ["Docker", "Kubernetes", "CI/CD"]
    
    def respond(self, user_input: str) -> str:
        """Override with DevOps-specific behavior."""
        self.add_message("user", user_input)
        
        relevant = [s for s in self.specialties if s.lower() in user_input.lower()]
        if relevant:
            response = f"As a DevOps expert in {', '.join(relevant)}, here's my answer..."
        else:
            response = f"Let me help with that DevOps question..."
        
        self.add_message("assistant", response)
        return response


class CodeAgent(BaseAgent):
    """Specialized agent for coding tasks."""
    
    def __init__(self, name: str, languages: list[str] | None = None):
        super().__init__(name, model="gpt-4")
        self.languages = languages or ["Python", "JavaScript", "Go"]
    
    def respond(self, user_input: str) -> str:
        self.add_message("user", user_input)
        response = f"I'll write that in one of these languages: {', '.join(self.languages)}"
        self.add_message("assistant", response)
        return response


# Usage
devops = DevOpsAgent("InfraBot", specialties=["Docker", "Terraform", "AWS"])
coder = CodeAgent("CodeBot")

print(devops)  # DevOpsAgent('InfraBot')
print(devops.respond("How to use Docker?"))
print(coder.respond("Build a REST API"))

# isinstance checks
print(isinstance(devops, BaseAgent))  # True
print(isinstance(devops, DevOpsAgent))  # True
print(isinstance(devops, CodeAgent))  # False
```

---

## 2. Method Resolution & super()

```python
class BaseAgent:
    def __init__(self, name: str):
        self.name = name
        self.tools: list[str] = []
        print(f"BaseAgent.__init__ called for {name}")
    
    def setup(self):
        print("BaseAgent.setup: Loading default tools")
        self.tools.append("search")

class AdvancedAgent(BaseAgent):
    def __init__(self, name: str, model: str):
        super().__init__(name)  # Call parent's __init__
        self.model = model
        print(f"AdvancedAgent.__init__ called for {name}")
    
    def setup(self):
        super().setup()  # Call parent's setup FIRST
        print("AdvancedAgent.setup: Loading advanced tools")
        self.tools.extend(["code_exec", "web_browser"])

agent = AdvancedAgent("SuperBot", "gpt-4")
agent.setup()
print(f"Tools: {agent.tools}")
# BaseAgent.__init__ called for SuperBot
# AdvancedAgent.__init__ called for SuperBot
# BaseAgent.setup: Loading default tools
# AdvancedAgent.setup: Loading advanced tools
# Tools: ['search', 'code_exec', 'web_browser']
```

---

## 3. Abstract Base Classes

```python
from abc import ABC, abstractmethod

class BaseTool(ABC):
    """Abstract base class — cannot be instantiated directly."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    def execute(self, input_data: str) -> str:
        """Subclasses MUST implement this method."""
        pass
    
    def __str__(self):
        return f"Tool({self.name})"

# tool = BaseTool("test", "test")  # ❌ TypeError: Can't instantiate abstract class

class SearchTool(BaseTool):
    def execute(self, input_data: str) -> str:
        return f"Searching for: {input_data}"

class CalculatorTool(BaseTool):
    def execute(self, input_data: str) -> str:
        try:
            result = eval(input_data, {"__builtins__": {}})
            return f"Result: {result}"
        except Exception as e:
            return f"Error: {e}"

class CodeExecutor(BaseTool):
    def __init__(self):
        super().__init__("code_executor", "Execute Python code snippets")
        self.allowed_builtins = {"print", "len", "range", "str", "int", "float"}
    
    def execute(self, input_data: str) -> str:
        return f"[Code execution simulated]: {input_data[:50]}..."

# Usage — all tools share the same interface
tools: list[BaseTool] = [
    SearchTool("search", "Search the web"),
    CalculatorTool("calc", "Do math"),
    CodeExecutor(),
]

for tool in tools:
    print(f"{tool}: {tool.execute('2 + 2')}")
```

---

## 4. Composition Over Inheritance

Inheritance = "is a" relationship. Composition = "has a" relationship.

```python
class Memory:
    """A memory component that any agent can use."""
    
    def __init__(self, max_items: int = 100):
        self.items: list[dict] = []
        self.max_items = max_items
    
    def store(self, key: str, value: str):
        if len(self.items) >= self.max_items:
            self.items.pop(0)
        self.items.append({"key": key, "value": value})
    
    def recall(self, key: str) -> str | None:
        for item in reversed(self.items):
            if item["key"] == key:
                return item["value"]
        return None
    
    def search(self, query: str) -> list[dict]:
        return [item for item in self.items if query.lower() in item["value"].lower()]


class ToolBelt:
    """A collection of tools that any agent can use."""
    
    def __init__(self):
        self.tools: dict[str, BaseTool] = {}
    
    def register(self, tool: BaseTool):
        self.tools[tool.name] = tool
    
    def execute(self, tool_name: str, input_data: str) -> str:
        if tool_name not in self.tools:
            return f"Tool '{tool_name}' not found"
        return self.tools[tool_name].execute(input_data)
    
    def list_tools(self) -> list[str]:
        return list(self.tools.keys())


class SmartAgent:
    """An agent composed of different components."""
    
    def __init__(self, name: str, model: str):
        self.name = name
        self.model = model
        self.memory = Memory()           # HAS a memory
        self.tool_belt = ToolBelt()      # HAS a tool belt
        self.messages: list[dict] = []   # HAS messages
    
    def equip_tool(self, tool: BaseTool):
        self.tool_belt.register(tool)
    
    def remember(self, key: str, value: str):
        self.memory.store(key, value)
    
    def recall(self, key: str) -> str | None:
        return self.memory.recall(key)
    
    def use_tool(self, tool_name: str, input_data: str) -> str:
        return self.tool_belt.execute(tool_name, input_data)
    
    def chat(self, message: str) -> str:
        self.messages.append({"role": "user", "content": message})
        
        # Check if message requests a tool
        if message.startswith("/use "):
            parts = message[5:].split(" ", 1)
            tool_name = parts[0]
            tool_input = parts[1] if len(parts) > 1 else ""
            response = self.use_tool(tool_name, tool_input)
        elif message.startswith("/remember "):
            parts = message[10:].split("=", 1)
            if len(parts) == 2:
                self.remember(parts[0].strip(), parts[1].strip())
                response = f"Remembered: {parts[0].strip()}"
            else:
                response = "Use format: /remember key=value"
        elif message.startswith("/recall "):
            key = message[8:].strip()
            value = self.recall(key)
            response = value if value else f"I don't remember '{key}'"
        else:
            response = f"[{self.model}] Processing: {message[:50]}..."
        
        self.messages.append({"role": "assistant", "content": response})
        return response

# Build a fully-equipped agent
agent = SmartAgent("DevBot", "gpt-4")
agent.equip_tool(SearchTool("search", "Search the web"))
agent.equip_tool(CalculatorTool("calc", "Calculate math"))

# Use it
print(agent.chat("Hello!"))
print(agent.chat("/use search Python AI agents"))
print(agent.chat("/use calc 2**10"))
print(agent.chat("/remember project=kubernetes-migration"))
print(agent.chat("/recall project"))
```

---

## 5. When to Use What

| Pattern | Use When | Example |
|---------|----------|---------|
| **Inheritance** | Objects ARE a type of parent | `DevOpsAgent(BaseAgent)` |
| **Composition** | Objects HAVE/USE components | `Agent` has a `Memory` |
| **Abstract classes** | Enforcing an interface | `BaseTool` with `execute()` |
| **Mixins** | Adding cross-cutting capabilities | `LoggingMixin`, `CachingMixin` |

### Mixin Example
```python
class LoggingMixin:
    def log(self, level: str, message: str):
        from datetime import datetime
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"[{ts}] [{level}] [{self.__class__.__name__}] {message}")

class CachingMixin:
    _cache: dict = {}
    
    def cache_set(self, key: str, value):
        self._cache[key] = value
    
    def cache_get(self, key: str, default=None):
        return self._cache.get(key, default)

class ProductionAgent(BaseAgent, LoggingMixin, CachingMixin):
    def respond(self, user_input: str) -> str:
        self.log("INFO", f"Received: {user_input[:30]}...")
        
        cached = self.cache_get(user_input)
        if cached:
            self.log("DEBUG", "Cache hit!")
            return cached
        
        response = f"Processing: {user_input}"
        self.cache_set(user_input, response)
        return response
```

---

## 6. Exercises

### Exercise 1: Agent Hierarchy
```python
# Create this hierarchy:
# BaseAgent (name, model)
#   ├── ChatAgent (personality, greeting)
#   ├── TaskAgent (task_queue, completed_tasks)
#   └── MultiAgent (sub_agents list, delegate method)
# Each should override respond() with different behavior
# Test with at least 2 instances of each
```

### Exercise 2: Plugin Architecture
```python
# Build a plugin system:
# 1. Create an abstract Plugin class with name, version, and execute() method
# 2. Create 3 concrete plugins: LoggerPlugin, ValidatorPlugin, TransformerPlugin
# 3. Create a PluginManager that can register, unregister, and run plugins
# 4. Plugins should run in order of registration
# Test the full pipeline
```

### Exercise 3: Composable Agent Builder
```python
# Build an AgentBuilder that uses composition:
# agent = (AgentBuilder("MyAgent")
#     .with_model("gpt-4")
#     .with_memory(max_items=50)
#     .with_tool(SearchTool("search", "Web search"))
#     .with_tool(CalculatorTool("calc", "Math"))
#     .with_system_prompt("You are a helpful assistant")
#     .build())
# Implement the builder pattern with method chaining
```

---

## Solutions

See [solutions/day12_solutions.py](../solutions/day12_solutions.py)

---

## Key Takeaways
- **Inheritance**: child class gets parent's attributes and methods; override to specialize
- **`super()`**: call the parent's version of a method
- **ABC**: abstract base classes enforce that subclasses implement required methods
- **Composition**: build complex objects from simpler components — prefer this over deep inheritance
- **Mixins**: add capabilities without inheritance hierarchies
- **Builder pattern**: method chaining for readable object construction

**Tomorrow:** Comprehensions, generators & lambdas →
