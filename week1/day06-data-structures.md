# Day 6: Lists, Tuples & Dictionaries

## Learning Goals
- Master list operations (add, remove, sort, search)
- Understand tuples and when to use them
- Work with dictionaries for key-value storage
- Combine data structures for real-world use cases

---

## 1. Lists — Ordered, Mutable Collections

```python
# Creating lists
models = ["GPT-4", "Claude", "Gemini"]
scores = [92.5, 91.8, 90.3]
mixed = ["agent", 42, True, 3.14]
empty = []

# Accessing elements
print(models[0])     # "GPT-4"
print(models[-1])    # "Gemini"
print(models[1:3])   # ["Claude", "Gemini"]

# Length
print(len(models))   # 3
```

### Modifying Lists
```python
tools = ["search", "calculator", "code"]

# Add elements
tools.append("memory")              # Add to end
tools.insert(0, "router")           # Insert at position 0
tools.extend(["browser", "email"])   # Add multiple items

print(tools)
# ['router', 'search', 'calculator', 'code', 'memory', 'browser', 'email']

# Remove elements
tools.remove("email")    # Remove by value (first occurrence)
last = tools.pop()       # Remove and return last item
first = tools.pop(0)     # Remove and return item at index 0
del tools[1]             # Delete by index

# Modify elements
tools[0] = "web_search"  # Replace element at index
```

### Sorting & Searching
```python
numbers = [3, 1, 4, 1, 5, 9, 2, 6]

# Sorting
numbers.sort()                    # Sort in place (ascending)
numbers.sort(reverse=True)       # Sort in place (descending)
sorted_nums = sorted(numbers)    # Return new sorted list (original unchanged)

# Searching
print(5 in numbers)              # True
print(numbers.index(5))          # Index of first occurrence
print(numbers.count(1))          # Count occurrences

# Min, Max, Sum
print(min(numbers))
print(max(numbers))
print(sum(numbers))
```

### List Copying (Important!)
```python
# ❌ This creates a REFERENCE, not a copy
original = [1, 2, 3]
reference = original
reference.append(4)
print(original)   # [1, 2, 3, 4] — original is modified!

# ✅ Proper copying
copy1 = original.copy()
copy2 = original[:]
copy3 = list(original)
```

---

## 2. Tuples — Ordered, Immutable Collections

```python
# Tuples use parentheses (or no brackets)
coordinates = (40.7128, -74.0060)
model_info = ("GPT-4", "OpenAI", 2023)
single = (42,)    # Note the comma for single-element tuple

# Accessing (same as lists)
print(model_info[0])       # "GPT-4"
print(model_info[1:])      # ("OpenAI", 2023)

# Unpacking
name, company, year = model_info
print(f"{name} by {company} ({year})")

# ❌ Cannot modify tuples
# coordinates[0] = 0  # TypeError!

# When to use tuples vs lists:
# Tuple: fixed data that shouldn't change (coordinates, RGB colors, config)
# List: dynamic collections that grow/shrink (messages, results, tools)
```

---

## 3. Dictionaries — Key-Value Storage

```python
# Creating dictionaries
agent = {
    "name": "DevOps Assistant",
    "model": "gpt-4o-mini",
    "temperature": 0.7,
    "tools": ["search", "code", "deploy"],
    "max_tokens": 4096
}

# Accessing values
print(agent["name"])            # "DevOps Assistant"
print(agent.get("model"))      # "gpt-4"
print(agent.get("missing", "default_value"))  # "default_value" (no KeyError)

# Modifying
agent["temperature"] = 0.3      # Update existing
agent["version"] = "2.0"        # Add new key
del agent["max_tokens"]         # Delete key

# Checking keys
print("name" in agent)          # True
print("missing" in agent)       # False
```

### Iterating Dictionaries
```python
config = {"model": "gpt-4", "temp": 0.7, "tokens": 2048}

# Keys
for key in config:
    print(key)

# Values
for value in config.values():
    print(value)

# Both
for key, value in config.items():
    print(f"{key}: {value}")
```

### Dictionary Methods
```python
d1 = {"a": 1, "b": 2}
d2 = {"b": 3, "c": 4}

# Merge (Python 3.9+)
merged = d1 | d2
print(merged)  # {'a': 1, 'b': 3, 'c': 4}  — d2 values win on conflicts

# Update in place
d1.update(d2)  # Same effect but modifies d1

# Get all keys/values
keys = list(config.keys())
values = list(config.values())

# Pop (remove and return)
temp = config.pop("temp")
print(temp)  # 0.7

# Set default (add if missing, return existing if present)
config.setdefault("model", "gpt-3.5")  # Already exists, returns "gpt-4"
config.setdefault("stream", False)      # Doesn't exist, adds it
```

---

## 4. Nested Data Structures

This is extremely common when working with AI APIs:

```python
# API response structure
chat_response = {
    "id": "chatcmpl-abc123",
    "model": "gpt-4",
    "choices": [
        {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "Hello! How can I help you today?"
            },
            "finish_reason": "stop"
        }
    ],
    "usage": {
        "prompt_tokens": 10,
        "completion_tokens": 9,
        "total_tokens": 19
    }
}

# Navigating nested data
content = chat_response["choices"][0]["message"]["content"]
total_tokens = chat_response["usage"]["total_tokens"]
print(f"Response: {content}")
print(f"Tokens used: {total_tokens}")

# Safe navigation with .get()
tool_calls = chat_response["choices"][0]["message"].get("tool_calls", [])
print(f"Tool calls: {tool_calls}")  # [] (empty, key doesn't exist)
```

---

## 5. Sets — Unique, Unordered Collections

```python
# Create a set
unique_tools = {"search", "code", "search", "deploy", "code"}
print(unique_tools)  # {'search', 'code', 'deploy'} — duplicates removed

# Set operations
set_a = {"search", "code", "deploy"}
set_b = {"code", "test", "monitor"}

print(set_a & set_b)   # {'code'}            — intersection
print(set_a | set_b)   # all five            — union
print(set_a - set_b)   # {'search', 'deploy'} — difference

# Practical: Find unique models in logs
api_calls = ["gpt-4", "gpt-3.5", "gpt-4", "claude", "gpt-4", "claude"]
unique_models = set(api_calls)
print(f"Unique models used: {unique_models}")
print(f"Count: {len(unique_models)}")
```

---

## 6. Practical: Conversation History Manager

```python
class ConversationManager:
    """Manages a chat conversation history using lists and dicts."""
    
    def __init__(self, system_prompt: str):
        self.messages: list[dict] = [
            {"role": "system", "content": system_prompt}
        ]
    
    def add_user_message(self, content: str):
        self.messages.append({"role": "user", "content": content})
    
    def add_assistant_message(self, content: str):
        self.messages.append({"role": "assistant", "content": content})
    
    def get_last_n(self, n: int) -> list[dict]:
        """Get the last n messages (always include system prompt)."""
        system = self.messages[0]
        recent = self.messages[-n:] if n < len(self.messages) else self.messages[1:]
        return [system] + recent
    
    def count_tokens_estimate(self) -> int:
        """Rough token estimate (4 chars per token)."""
        total_chars = sum(len(m["content"]) for m in self.messages)
        return total_chars // 4
    
    def display(self):
        for msg in self.messages:
            role = msg["role"].upper()
            content = msg["content"][:80]
            print(f"[{role}] {content}")

# Usage
convo = ConversationManager("You are a helpful DevOps assistant.")
convo.add_user_message("How do I create a Docker container?")
convo.add_assistant_message("You can create a Docker container using `docker run`...")
convo.add_user_message("What about docker-compose?")
convo.add_assistant_message("Docker Compose lets you define multi-container apps...")

convo.display()
print(f"\nEstimated tokens: {convo.count_tokens_estimate()}")
print(f"\nLast 2 messages: {convo.get_last_n(2)}")
```

---

## 7. Exercises

### Exercise 1: Model Leaderboard
```python
# Given this data:
models = [
    {"name": "GPT-4", "score": 92.5, "cost": 0.03, "provider": "OpenAI"},
    {"name": "Claude-3", "score": 91.8, "cost": 0.015, "provider": "Anthropic"},
    {"name": "Gemini", "score": 90.3, "cost": 0.001, "provider": "Google"},
    {"name": "GPT-3.5", "score": 85.2, "cost": 0.002, "provider": "OpenAI"},
    {"name": "LLaMA-3", "score": 88.7, "cost": 0.0, "provider": "Meta"},
]
# 1. Sort by score (highest first) and print a ranked table
# 2. Find all models from OpenAI
# 3. Find the cheapest model
# 4. Find models with score > 90
# 5. Calculate average score across all models
# 6. Create a dict mapping provider → list of model names
```

### Exercise 2: Inventory Tracker
```python
# Build an interactive inventory system using a dict:
# - add(item, quantity) — add or update quantity
# - remove(item, quantity) — reduce quantity (don't go below 0)
# - check(item) — print current quantity
# - list_all() — print all items and quantities
# - low_stock(threshold=5) — print items below threshold
# Test with a main loop that takes commands
```

### Exercise 3: Message Deduplicator
```python
# Given a list of messages with possible duplicates:
messages = [
    {"id": 1, "text": "Hello", "timestamp": "10:00"},
    {"id": 2, "text": "How are you?", "timestamp": "10:01"},
    {"id": 1, "text": "Hello", "timestamp": "10:02"},  # duplicate id
    {"id": 3, "text": "Help me", "timestamp": "10:03"},
    {"id": 2, "text": "How are you?", "timestamp": "10:04"},  # duplicate id
]
# Remove duplicates (keep first occurrence based on id)
# Print the deduplicated list
```

---

## Solutions

See [solutions/day06_solutions.py](../solutions/day06_solutions.py)

---

## Key Takeaways
- **Lists**: ordered, mutable — use for collections that change (`append`, `pop`, `sort`)
- **Tuples**: ordered, immutable — use for fixed data (coordinates, configs)
- **Dicts**: key-value pairs — use for structured data (configs, API responses)
- **Sets**: unique, unordered — use for deduplication and membership testing
- Use `.get(key, default)` to safely access dict keys
- Nested structures (lists of dicts) are the norm in AI API work
- `copy()` or `[:]` to avoid unintended mutations

**Tomorrow:** Mini-Project — CLI Chatbot Skeleton →
