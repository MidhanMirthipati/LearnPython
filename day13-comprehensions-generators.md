# Day 13: List Comprehensions, Generators & Lambdas

## Learning Goals
- Write concise list/dict/set comprehensions
- Use generators for memory-efficient iteration
- Use lambda functions for short operations
- Apply functional patterns: map, filter, sorted

---

## 1. List Comprehensions

```python
# Traditional loop
squares = []
for x in range(10):
    squares.append(x ** 2)

# List comprehension (same result, one line)
squares = [x ** 2 for x in range(10)]
print(squares)  # [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

# With condition (filter)
even_squares = [x ** 2 for x in range(10) if x % 2 == 0]
print(even_squares)  # [0, 4, 16, 36, 64]

# With transformation
models = ["gpt-4", "claude-3", "gemini"]
upper_models = [m.upper() for m in models]
print(upper_models)  # ['GPT-4', 'CLAUDE-3', 'GEMINI']

# With if/else (expression, not filter)
labels = ["EXPENSIVE" if cost > 0.01 else "CHEAP" 
          for cost in [0.03, 0.002, 0.015, 0.001]]
print(labels)  # ['EXPENSIVE', 'CHEAP', 'EXPENSIVE', 'CHEAP']
```

### AI-Practical Examples
```python
# Extract just the content from messages
messages = [
    {"role": "system", "content": "You are a helper"},
    {"role": "user", "content": "What is Docker?"},
    {"role": "assistant", "content": "Docker is..."},
]
contents = [m["content"] for m in messages if m["role"] != "system"]
print(contents)  # ['What is Docker?', 'Docker is...']

# Estimate tokens for each message
token_counts = [len(m["content"].split()) for m in messages]
print(token_counts)  # [4, 3, 2]

# Filter long messages
long_messages = [m for m in messages if len(m["content"]) > 10]
```

---

## 2. Dictionary Comprehensions

```python
# Create a dict from two lists
models = ["gpt-4", "claude-3", "gemini"]
scores = [92.5, 91.8, 90.3]

model_scores = {model: score for model, score in zip(models, scores)}
print(model_scores)  # {'gpt-4': 92.5, 'claude-3': 91.8, 'gemini': 90.3}

# Transform a dict
costs = {"gpt-4": 0.03, "claude": 0.015, "gemini": 0.001}
costs_per_million = {model: cost * 1_000_000 for model, cost in costs.items()}
print(costs_per_million)  # {'gpt-4': 30000.0, 'claude': 15000.0, 'gemini': 1000.0}

# Filter a dict
affordable = {m: c for m, c in costs.items() if c < 0.01}
print(affordable)  # {'gemini': 0.001}

# Invert a dict
score_to_model = {v: k for k, v in model_scores.items()}
```

---

## 3. Set Comprehensions

```python
# Unique word lengths
sentence = "the quick brown fox jumps over the lazy dog"
word_lengths = {len(word) for word in sentence.split()}
print(word_lengths)  # {3, 4, 5}

# Unique roles in messages
messages = [
    {"role": "user", "content": "hi"},
    {"role": "assistant", "content": "hello"},
    {"role": "user", "content": "help"},
]
roles = {m["role"] for m in messages}
print(roles)  # {'user', 'assistant'}
```

---

## 4. Generators

Generators produce values one at a time — memory efficient for large datasets.

```python
# Generator expression (like comprehension but with parentheses)
squares_gen = (x ** 2 for x in range(1_000_000))
print(type(squares_gen))    # <class 'generator'>

# Only computes values as needed
print(next(squares_gen))    # 0
print(next(squares_gen))    # 1
print(next(squares_gen))    # 4

# Works in for loops
for square in (x ** 2 for x in range(5)):
    print(square)

# Useful with sum, min, max (no intermediate list created)
total = sum(x ** 2 for x in range(1_000_000))  # Memory efficient!
```

### Generator Functions (yield)
```python
def token_batcher(messages: list[str], batch_size: int = 3):
    """Yield messages in batches."""
    batch = []
    for msg in messages:
        batch.append(msg)
        if len(batch) == batch_size:
            yield batch
            batch = []
    if batch:  # Don't forget the last partial batch
        yield batch

messages = ["msg1", "msg2", "msg3", "msg4", "msg5", "msg6", "msg7"]
for batch in token_batcher(messages, batch_size=3):
    print(f"Processing batch: {batch}")
# Processing batch: ['msg1', 'msg2', 'msg3']
# Processing batch: ['msg4', 'msg5', 'msg6']
# Processing batch: ['msg7']
```

### Practical Generator: Log Stream
```python
def read_log_stream(filepath: str):
    """Read a log file line by line (memory efficient for huge files)."""
    with open(filepath, "r") as f:
        for line_num, line in enumerate(f, 1):
            yield {
                "line": line_num,
                "level": line[1:line.index("]")] if line.startswith("[") else "UNKNOWN",
                "content": line.strip()
            }

def filter_errors(log_stream):
    """Filter for only ERROR entries."""
    for entry in log_stream:
        if entry["level"] == "ERROR":
            yield entry

# Chain generators — like Unix pipes
# errors = filter_errors(read_log_stream("agent.log"))
# for error in errors:
#     print(f"Line {error['line']}: {error['content']}")
```

---

## 5. Lambda Functions

```python
# Lambda = anonymous one-line function
square = lambda x: x ** 2
print(square(5))  # 25

add = lambda a, b: a + b
print(add(3, 4))  # 7

# Primarily used as arguments to other functions
models = [
    {"name": "GPT-4", "score": 92.5, "cost": 0.03},
    {"name": "Claude", "score": 91.8, "cost": 0.015},
    {"name": "Gemini", "score": 90.3, "cost": 0.001},
]

# Sort by score (descending)
by_score = sorted(models, key=lambda m: m["score"], reverse=True)

# Sort by cost (ascending)
by_cost = sorted(models, key=lambda m: m["cost"])

# Sort by cost-efficiency (score per dollar)
by_efficiency = sorted(models, key=lambda m: m["score"] / m["cost"], reverse=True)

for m in by_efficiency:
    eff = m["score"] / m["cost"]
    print(f"{m['name']}: {eff:.0f} score/$")
```

---

## 6. map(), filter(), reduce()

```python
# map() — apply function to every element
prompts = ["  hello  ", "  WORLD  ", "  Python  "]
cleaned = list(map(str.strip, prompts))
print(cleaned)  # ['hello', 'WORLD', 'Python']

token_counts = list(map(lambda p: len(p.split()), cleaned))
print(token_counts)  # [1, 1, 1]

# filter() — keep elements that pass the test
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
evens = list(filter(lambda x: x % 2 == 0, numbers))
print(evens)  # [2, 4, 6, 8, 10]

# Most Pythonic: use comprehensions instead
evens = [x for x in numbers if x % 2 == 0]

# reduce() — accumulate into a single value
from functools import reduce
total = reduce(lambda acc, x: acc + x, numbers)
print(total)  # 55
# Better: just use sum(numbers)
```

---

## 7. Practical: Message Processing Pipeline

```python
from datetime import datetime

# Raw messages from an API
raw_messages = [
    {"role": "user", "content": "  How do I use docker?  ", "timestamp": "2024-01-15T10:30:00"},
    {"role": "assistant", "content": "Docker is a containerization platform.  ", "timestamp": "2024-01-15T10:30:05"},
    {"role": "user", "content": "", "timestamp": "2024-01-15T10:31:00"},  # empty
    {"role": "system", "content": "You are a helpful assistant.", "timestamp": "2024-01-15T10:00:00"},
    {"role": "user", "content": "  What about Kubernetes?  ", "timestamp": "2024-01-15T10:32:00"},
    {"role": "assistant", "content": "Kubernetes orchestrates containers.  ", "timestamp": "2024-01-15T10:32:05"},
]

# Pipeline using comprehensions and generators

# Step 1: Clean whitespace
cleaned = [
    {**msg, "content": msg["content"].strip()}
    for msg in raw_messages
]

# Step 2: Remove empty messages
non_empty = [msg for msg in cleaned if msg["content"]]

# Step 3: Separate by role
user_messages = [msg for msg in non_empty if msg["role"] == "user"]
assistant_messages = [msg for msg in non_empty if msg["role"] == "assistant"]

# Step 4: Token estimates
token_estimates = {
    msg["content"][:30]: len(msg["content"].split())
    for msg in non_empty
    if msg["role"] != "system"
}

# Step 5: Build analytics
analytics = {
    "total_messages": len(non_empty),
    "user_messages": len(user_messages),
    "assistant_messages": len(assistant_messages),
    "total_tokens": sum(len(m["content"].split()) for m in non_empty),
    "avg_tokens_per_message": round(
        sum(len(m["content"].split()) for m in non_empty) / len(non_empty), 1
    ),
    "unique_topics": len({m["content"].split()[0].lower() for m in user_messages}),
}

# Print results
print("=== Message Analytics ===")
for key, value in analytics.items():
    print(f"  {key}: {value}")

print("\n=== Token Estimates ===")
for content, tokens in token_estimates.items():
    print(f"  '{content}...': ~{tokens} tokens")
```

---

## 8. Exercises

### Exercise 1: Data Transformer
```python
# Given this API response data:
api_data = [
    {"id": 1, "model": "gpt-4", "tokens": 150, "cost": 0.0045, "status": "success"},
    {"id": 2, "model": "gpt-3.5", "tokens": 200, "cost": 0.0004, "status": "success"},
    {"id": 3, "model": "gpt-4", "tokens": 50, "cost": 0.0015, "status": "error"},
    {"id": 4, "model": "claude", "tokens": 300, "cost": 0.0045, "status": "success"},
    {"id": 5, "model": "gpt-4", "tokens": 100, "cost": 0.003, "status": "success"},
    {"id": 6, "model": "claude", "tokens": 175, "cost": 0.002625, "status": "error"},
]
# Using comprehensions, compute:
# 1. List of successful requests only
# 2. Total tokens for gpt-4 model requests
# 3. Dict of model → total cost
# 4. Average tokens per request (successful only)
# 5. List of (id, cost_per_token) tuples, sorted by cost_per_token
# 6. Set of unique models used
```

### Exercise 2: Generator Pipeline
```python
# Build a generator pipeline for processing chat logs:
# 1. read_lines(text) — yields lines one at a time
# 2. parse_entries(lines) — yields parsed dicts {timestamp, level, message}
# 3. filter_level(entries, level) — yields entries matching level
# 4. format_output(entries) — yields formatted strings
# Chain them together and process this log:
log_text = """
2024-01-15 10:00:00 INFO Agent started
2024-01-15 10:00:01 DEBUG Loading tools
2024-01-15 10:00:05 INFO Processing request
2024-01-15 10:00:06 ERROR API timeout
2024-01-15 10:00:10 INFO Retrying
2024-01-15 10:00:11 INFO Request complete
2024-01-15 10:00:15 WARNING Token usage high
"""
```

### Exercise 3: Comprehension Challenge
```python
# Solve each in a single comprehension:
# 1. Flatten: [[1,2],[3,4],[5,6]] → [1,2,3,4,5,6]
# 2. Create a multiplication table (dict): {(i,j): i*j for 1-5}
# 3. Find all words > 5 letters in a paragraph (use a set comprehension)
# 4. Create {word: len(word)} for all unique words in a sentence
# 5. Transpose a matrix: [[1,2,3],[4,5,6]] → [[1,4],[2,5],[3,6]]
```

---

## Solutions

See [solutions/day13_solutions.py](../solutions/day13_solutions.py)

---

## Key Takeaways
- **List comprehensions**: `[expr for x in iterable if condition]` — concise and fast
- **Dict comprehensions**: `{k: v for k, v in iterable}` — great for transformations
- **Generators**: `(expr for x in iterable)` or `yield` — memory efficient for large data
- **Lambdas**: `lambda x: expr` — anonymous functions for `sorted()`, `map()`, `filter()`
- Prefer comprehensions over `map()`/`filter()` for readability
- Chain generators like Unix pipes for processing pipelines

**Tomorrow:** Mini-Project — Conversation Logger with OOP →
