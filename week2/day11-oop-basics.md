# Day 11: Object-Oriented Programming — Basics

## Learning Goals
- Understand classes and objects
- Define attributes and methods
- Use `__init__`, `__str__`, `__repr__`
- Build an Agent class from scratch

---

## 1. What Are Classes and Objects?

A **class** is a blueprint. An **object** is a thing built from that blueprint.

```python
# Class = blueprint for an AI Agent
# Object = a specific agent like "DevOps Bot" or "Code Reviewer"

class Agent:
    pass  # Empty class for now

# Create objects (instances) from the class
agent1 = Agent()
agent2 = Agent()
print(type(agent1))  # <class '__main__.Agent'>
```

---

## 2. The `__init__` Method (Constructor)

```python
class Agent:
    def __init__(self, name: str, model: str, temperature: float = 0.7):
        """Initialize a new Agent."""
        self.name = name                # Instance attribute
        self.model = model
        self.temperature = temperature
        self.messages = []              # Every agent gets its own message list
        self.total_tokens = 0

# Create agents
bot1 = Agent("DevBot", "gpt-4")
bot2 = Agent("CodeReviewer", "claude-3", temperature=0.2)

print(bot1.name)          # "DevBot"
print(bot2.temperature)   # 0.2
```

### What is `self`?
```python
# 'self' refers to the specific object being created/used
# When you call Agent("DevBot", "gpt-4"), Python does:
# Agent.__init__(new_object, "DevBot", "gpt-4")
# 'self' IS that new_object
```

---

## 3. Methods

```python
class Agent:
    def __init__(self, name: str, model: str):
        self.name = name
        self.model = model
        self.messages: list[dict] = []
    
    def add_message(self, role: str, content: str):
        """Add a message to the conversation."""
        self.messages.append({"role": role, "content": content})
    
    def get_last_message(self) -> dict | None:
        """Return the last message, or None if empty."""
        return self.messages[-1] if self.messages else None
    
    def clear_history(self):
        """Clear all messages."""
        self.messages.clear()
    
    def message_count(self) -> int:
        """Return the number of messages."""
        return len(self.messages)

# Usage
bot = Agent("DevBot", "gpt-4")
bot.add_message("user", "How do I use Docker?")
bot.add_message("assistant", "Docker is a containerization platform...")
print(bot.message_count())      # 2
print(bot.get_last_message())   # {'role': 'assistant', 'content': '...'}
```

---

## 4. Special (Dunder) Methods

```python
class Agent:
    def __init__(self, name: str, model: str):
        self.name = name
        self.model = model
        self.messages: list[dict] = []
    
    def __str__(self) -> str:
        """Human-readable string (used by print())."""
        return f"Agent '{self.name}' using {self.model}"
    
    def __repr__(self) -> str:
        """Developer-readable string (used in debugger/REPL)."""
        return f"Agent(name='{self.name}', model='{self.model}')"
    
    def __len__(self) -> int:
        """Allow len(agent) to return message count."""
        return len(self.messages)
    
    def __bool__(self) -> bool:
        """Agent is 'truthy' if it has messages."""
        return len(self.messages) > 0

bot = Agent("DevBot", "gpt-4")
print(bot)          # Agent 'DevBot' using gpt-4
print(repr(bot))    # Agent(name='DevBot', model='gpt-4')
print(len(bot))     # 0
print(bool(bot))    # False

bot.messages.append({"role": "user", "content": "hi"})
print(bool(bot))    # True
```

---

## 5. Class vs Instance Attributes

```python
class Agent:
    # Class attributes — shared by ALL instances
    agent_count = 0
    DEFAULT_MODEL = "gpt-3.5-turbo"
    
    def __init__(self, name: str, model: str | None = None):
        # Instance attributes — unique to each instance
        self.name = name
        self.model = model or Agent.DEFAULT_MODEL
        Agent.agent_count += 1  # Modify class attribute
    
    @classmethod
    def get_count(cls) -> int:
        """Class method — accesses class attributes via cls."""
        return cls.agent_count
    
    @staticmethod
    def is_valid_model(model: str) -> bool:
        """Static method — doesn't access self or cls."""
        valid = ["gpt-4", "gpt-3.5-turbo", "claude-3"]
        return model in valid

# Usage
a1 = Agent("Bot1")
a2 = Agent("Bot2", "gpt-4")
a3 = Agent("Bot3")

print(Agent.get_count())           # 3
print(Agent.is_valid_model("gpt-4"))  # True
print(a1.model)                    # "gpt-3.5-turbo" (default)
```

---

## 6. Properties

```python
class Agent:
    def __init__(self, name: str, temperature: float = 0.7):
        self.name = name
        self._temperature = temperature  # Private convention (underscore)
    
    @property
    def temperature(self) -> float:
        """Getter — called when you access agent.temperature."""
        return self._temperature
    
    @temperature.setter
    def temperature(self, value: float):
        """Setter — called when you assign agent.temperature = x."""
        if not 0.0 <= value <= 2.0:
            raise ValueError(f"Temperature must be 0.0-2.0, got {value}")
        self._temperature = value

bot = Agent("DevBot")
print(bot.temperature)    # 0.7  (uses getter)
bot.temperature = 0.3     # Uses setter
print(bot.temperature)    # 0.3

try:
    bot.temperature = 5.0  # Raises ValueError
except ValueError as e:
    print(f"Error: {e}")
```

---

## 7. Practical: Complete Agent Class

```python
from datetime import datetime
import json

class AIAgent:
    """A complete AI agent with conversation management."""
    
    def __init__(self, name: str, model: str = "gpt-3.5-turbo",
                 system_prompt: str = "You are a helpful assistant.",
                 temperature: float = 0.7, max_tokens: int = 2048):
        self.name = name
        self.model = model
        self._temperature = temperature
        self.max_tokens = max_tokens
        self.created_at = datetime.now()
        self.messages: list[dict] = [
            {"role": "system", "content": system_prompt}
        ]
        self.total_tokens_used = 0
        self.request_count = 0
    
    @property
    def temperature(self) -> float:
        return self._temperature
    
    @temperature.setter
    def temperature(self, value: float):
        if not 0.0 <= value <= 2.0:
            raise ValueError(f"Temperature must be 0.0-2.0, got {value}")
        self._temperature = value
    
    def chat(self, user_message: str) -> str:
        """Send a message and get a response (simulated)."""
        self.messages.append({"role": "user", "content": user_message})
        
        # Simulated response (replace with real API call later)
        response = f"[{self.model}] I received your message about: {user_message[:50]}..."
        self.messages.append({"role": "assistant", "content": response})
        
        # Update stats
        self.request_count += 1
        self.total_tokens_used += len(user_message.split()) + len(response.split())
        
        return response
    
    def get_stats(self) -> dict:
        """Get agent usage statistics."""
        return {
            "name": self.name,
            "model": self.model,
            "uptime": str(datetime.now() - self.created_at),
            "total_messages": len(self.messages),
            "requests": self.request_count,
            "tokens_used": self.total_tokens_used,
        }
    
    def export_conversation(self, filepath: str):
        """Export conversation to JSON file."""
        data = {
            "agent": self.name,
            "model": self.model,
            "exported_at": datetime.now().isoformat(),
            "messages": self.messages
        }
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
    
    def __str__(self) -> str:
        return f"AIAgent('{self.name}', model={self.model}, messages={len(self.messages)})"
    
    def __repr__(self) -> str:
        return f"AIAgent(name='{self.name}', model='{self.model}')"

# Usage
agent = AIAgent(
    name="DevOps Helper",
    model="gpt-4",
    system_prompt="You are an expert DevOps engineer.",
    temperature=0.3
)

print(agent)

response = agent.chat("How do I set up GitHub Actions for CI/CD?")
print(f"\nResponse: {response}")

response = agent.chat("What about Docker multi-stage builds?")
print(f"\nResponse: {response}")

print(f"\nStats: {json.dumps(agent.get_stats(), indent=2)}")
```

---

## 8. Exercises

### Exercise 1: Tool Class
```python
# Create a Tool class with:
# - name, description, required_params (list)
# - execute(params: dict) method that validates required params are present
# - __str__ that shows name and description
# Create at least 3 tool instances (search, calculator, weather)
# Test execution with valid and missing params
```

### Exercise 2: TokenTracker Class
```python
# Create a TokenTracker class that:
# - Tracks token usage per model
# - Has methods: add_usage(model, tokens), get_total(), get_by_model()
# - Has a budget attribute and budget_remaining property
# - Raises an error if usage would exceed budget
# - Has __str__ showing a usage summary table
```

### Exercise 3: ChatSession Class
```python
# Create a ChatSession class that:
# - Takes agent_name and system_prompt in __init__
# - Has send(message) method that adds user message and generates a mock response
# - Has undo() method that removes the last exchange (user + assistant)
# - Has search(keyword) method that finds messages containing keyword
# - Has summary property that returns count of user/assistant messages
# - Supports len() returning message count
# - Can be used in a bool context (True if has messages)
```

---

## Solutions

See [solutions/day11_solutions.py](../solutions/day11_solutions.py)

---

## Key Takeaways
- Classes define blueprints; objects are instances
- `__init__` initializes each new object; `self` refers to the instance
- Methods are functions that belong to a class and can access `self`
- Dunder methods (`__str__`, `__len__`, etc.) customize built-in behavior
- Use `@property` for controlled attribute access
- `@classmethod` for class-level operations; `@staticmethod` for utility functions
- OOP is essential for building structured AI agents

**Tomorrow:** OOP — Inheritance & composition →
