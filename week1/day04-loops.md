# Day 4: Loops & Iteration

## Learning Goals
- Use `for` and `while` loops
- Control loops with `break`, `continue`, `else`
- Use `range()` and `enumerate()`
- Nest loops and avoid common pitfalls

---

## 1. for Loops

```python
# Iterating over a list
models = ["GPT-4", "Claude", "Gemini", "LLaMA"]
for model in models:
    print(f"Model: {model}")

# Iterating over a string
for char in "Agent":
    print(char)
# A, g, e, n, t (each on its own line)

# Iterating over a range of numbers
for i in range(5):        # 0, 1, 2, 3, 4
    print(i)

for i in range(1, 6):     # 1, 2, 3, 4, 5
    print(i)

for i in range(0, 10, 2): # 0, 2, 4, 6, 8  (step of 2)
    print(i)

for i in range(5, 0, -1): # 5, 4, 3, 2, 1  (countdown)
    print(i)
```

---

## 2. while Loops

```python
# Basic while loop
count = 0
while count < 5:
    print(f"Count: {count}")
    count += 1

# Practical: Retry logic (common in API calls)
import random

attempts = 0
max_attempts = 5
success = False

while attempts < max_attempts and not success:
    attempts += 1
    print(f"Attempt {attempts}...")
    
    # Simulate API call (30% chance of success)
    if random.random() > 0.7:
        success = True
        print("✅ Success!")

if not success:
    print("❌ All attempts failed")
```

### ⚠️ Avoid Infinite Loops
```python
# DANGEROUS — this runs forever:
# while True:
#     print("Help!")

# SAFE — always have an exit condition:
while True:
    user_input = input("Type 'quit' to exit: ")
    if user_input.lower() == "quit":
        break
    print(f"You said: {user_input}")
```

---

## 3. break, continue, else

```python
# break — exit the loop immediately
for num in range(1, 100):
    if num == 5:
        print("Found 5, stopping!")
        break
    print(num)
# Prints: 1, 2, 3, 4, Found 5, stopping!

# continue — skip to the next iteration
for num in range(1, 6):
    if num == 3:
        continue    # Skip 3
    print(num)
# Prints: 1, 2, 4, 5

# else on a loop — runs if loop completed WITHOUT break
for num in [2, 4, 6, 8]:
    if num % 2 != 0:
        print(f"{num} is odd!")
        break
else:
    print("All numbers were even!")
# Prints: "All numbers were even!"
```

---

## 4. enumerate() — Index + Value

```python
models = ["GPT-4", "Claude-3", "Gemini", "LLaMA-3"]

# Without enumerate (anti-pattern)
for i in range(len(models)):
    print(f"{i}: {models[i]}")

# With enumerate (Pythonic ✅)
for index, model in enumerate(models):
    print(f"{index}: {model}")

# Custom start index
for rank, model in enumerate(models, start=1):
    print(f"Rank {rank}: {model}")
# Rank 1: GPT-4
# Rank 2: Claude-3
# ...
```

---

## 5. zip() — Parallel Iteration

```python
models = ["GPT-4", "Claude-3", "Gemini"]
scores = [92.5, 91.8, 90.3]
costs  = [0.03, 0.015, 0.001]

for model, score, cost in zip(models, scores, costs):
    print(f"{model}: Score={score}%, Cost=${cost}")
```

---

## 6. Nested Loops

```python
# Multiplication table
for i in range(1, 4):
    for j in range(1, 4):
        print(f"{i} x {j} = {i*j}", end="  ")
    print()  # New line after each row

# Practical: Comparing models on benchmarks
models = ["GPT-4", "Claude"]
benchmarks = ["MMLU", "HumanEval", "GSM8K"]

for model in models:
    print(f"\n--- {model} ---")
    for bench in benchmarks:
        print(f"  Testing on {bench}...")
```

---

## 7. Looping Over Dictionaries

```python
agent_config = {
    "name": "DevOps Bot",
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 2048
}

# Loop over keys
for key in agent_config:
    print(key)

# Loop over values
for value in agent_config.values():
    print(value)

# Loop over key-value pairs
for key, value in agent_config.items():
    print(f"{key}: {value}")
```

---

## 8. Common Loop Patterns

### Pattern 1: Accumulator
```python
# Sum all token counts
token_counts = [1500, 2300, 800, 4200, 1100]
total = 0
for count in token_counts:
    total += count
print(f"Total tokens: {total}")

# Python shortcut:
print(f"Total tokens: {sum(token_counts)}")
```

### Pattern 2: Filter and Collect
```python
# Find all models under budget
models = [
    {"name": "GPT-4", "cost": 0.03},
    {"name": "GPT-3.5", "cost": 0.002},
    {"name": "Claude-3", "cost": 0.015},
    {"name": "Gemini", "cost": 0.001},
]

budget = 0.01
affordable = []
for model in models:
    if model["cost"] <= budget:
        affordable.append(model["name"])

print(f"Affordable models: {affordable}")
```

### Pattern 3: Search
```python
# Find first model with a specific feature
models = [
    {"name": "GPT-4", "vision": True},
    {"name": "Claude", "vision": True},
    {"name": "GPT-3.5", "vision": False},
]

for model in models:
    if model["vision"]:
        print(f"First vision model: {model['name']}")
        break
```

### Pattern 4: Input Validation Loop
```python
while True:
    temp = input("Enter temperature (0.0 to 2.0): ")
    try:
        temp = float(temp)
        if 0.0 <= temp <= 2.0:
            print(f"Temperature set to {temp}")
            break
        else:
            print("Must be between 0.0 and 2.0")
    except ValueError:
        print("Please enter a valid number")
```

---

## 9. Exercises

### Exercise 1: Token Counter
```python
# Given a list of messages, count total "tokens" (approximate: word count)
messages = [
    "Hello, how are you today?",
    "I need help deploying a Kubernetes cluster on AWS",
    "Can you write a Python script to parse JSON logs?",
    "What is the difference between Docker and Podman?",
    "Explain CI/CD pipelines in simple terms"
]
# 1. Loop through messages and count words in each
# 2. Print each message with its word count
# 3. Print total "token" count
# 4. Print the average tokens per message
```

### Exercise 2: Retry Simulator
```python
# Simulate calling an unreliable API:
# 1. Max 5 retries
# 2. Each retry has a random chance of success (use random.random())
#    - Attempt 1: 20% chance
#    - Attempt 2: 40% chance  
#    - Attempt 3: 60% chance
#    - Attempt 4: 80% chance
#    - Attempt 5: 95% chance
# 3. Print each attempt and whether it succeeded or failed
# 4. If success, print "Connected on attempt X" and stop
# 5. If all fail, print "Service unavailable"
# 6. Add exponential backoff reporting: 1s, 2s, 4s, 8s, 16s
```

### Exercise 3: Number Guessing Game
```python
# 1. Generate a random number between 1 and 100
# 2. Let the user guess up to 7 times
# 3. After each guess, say "Too high" or "Too low"
# 4. If they guess correctly, print "You got it in X tries!"
# 5. If they run out of guesses, reveal the number
# Hint: import random; number = random.randint(1, 100)
```

---

## Solutions

See [solutions/day04_solutions.py](../solutions/day04_solutions.py)

---

## Key Takeaways
- `for` loops iterate over sequences; `while` loops run until a condition is false
- `range(start, stop, step)` generates number sequences
- `enumerate()` gives index + value; `zip()` iterates multiple lists in parallel
- `break` exits; `continue` skips; `else` on a loop runs if no `break`
- Common patterns: accumulator, filter, search, input validation
- Always ensure `while` loops have a reachable exit condition

**Tomorrow:** Functions and scope →
