# Day 2: Strings, Input & Output

## Learning Goals
- Master string operations and methods
- Take user input from the terminal
- Format output professionally
- Build an interactive greeting program

---

## 1. String Basics

```python
# Strings can use single or double quotes
greeting = 'Hello'
name = "World"

# Triple quotes for multi-line
description = """This is a
multi-line string that preserves
line breaks."""

# String length
message = "AI Agent"
print(len(message))  # 8

# Accessing characters (0-indexed)
print(message[0])    # A
print(message[3])    # A (space is index 2)
print(message[-1])   # t (last character)
```

---

## 2. String Slicing

```python
text = "Artificial Intelligence"

# text[start:end]  — end is exclusive
print(text[0:10])    # "Artificial"
print(text[11:23])   # "Intelligence"

# Shortcuts
print(text[:10])     # "Artificial"  (start from 0)
print(text[11:])     # "Intelligence" (go to end)
print(text[-12:])    # "Intelligence" (last 12 chars)

# Step
print(text[::2])     # "Atfca nelgne" (every 2nd char)
print(text[::-1])    # "ecnegilletnI laicifitrA" (reversed)
```

---

## 3. String Methods

```python
prompt = "  Hello, I am an AI Assistant!  "

# Case methods
print(prompt.upper())        # "  HELLO, I AM AN AI ASSISTANT!  "
print(prompt.lower())        # "  hello, i am an ai assistant!  "
print(prompt.title())        # "  Hello, I Am An Ai Assistant!  "

# Whitespace
print(prompt.strip())        # "Hello, I am an AI Assistant!"
print(prompt.lstrip())       # "Hello, I am an AI Assistant!  "
print(prompt.rstrip())       # "  Hello, I am an AI Assistant!"

# Find and Replace
print(prompt.find("AI"))     # 16  (index where "AI" starts)
print(prompt.replace("AI", "ML"))  # "  Hello, I am an ML Assistant!  "
print(prompt.count("a"))     # 2

# Checking content
print("AI" in prompt)        # True
print(prompt.strip().startswith("Hello"))  # True
print(prompt.strip().endswith("!"))        # True

# Splitting and joining
csv_line = "name,age,role,model"
parts = csv_line.split(",")
print(parts)                 # ['name', 'age', 'role', 'model']

words = ["GPT", "Claude", "Gemini"]
joined = " | ".join(words)
print(joined)                # "GPT | Claude | Gemini"
```

---

## 4. String Formatting Deep Dive

```python
# Method 1: f-strings (PREFERRED - Python 3.6+)
model = "GPT-4"
tokens = 8192
print(f"Model: {model}, Max Tokens: {tokens}")

# Formatting numbers
price = 0.00003
print(f"Cost: ${price:.5f}")          # Cost: $0.00003
print(f"Cost: ${price:.2e}")          # Cost: $3.00e-05

big_number = 1760000000000
print(f"Parameters: {big_number:,}")  # Parameters: 1,760,000,000,000

# Padding and alignment
for model in ["GPT-4", "Claude", "Gemini Pro"]:
    score = 92.5
    print(f"{model:<15} | Score: {score:>6.1f}%")
# GPT-4           | Score:   92.5%
# Claude          | Score:   92.5%
# Gemini Pro      | Score:   92.5%

# Method 2: .format() (older but still used)
template = "Hello, {}! You are using {}.".format("User", "Python")
print(template)
```

---

## 5. User Input

```python
# input() always returns a string
name = input("What is your name? ")
print(f"Hello, {name}!")

# Convert input to numbers
age = int(input("Enter your age: "))
print(f"In 10 years you will be {age + 10}")

# Handling potential errors (preview of Day 9)
try:
    number = int(input("Enter a number: "))
    print(f"Double: {number * 2}")
except ValueError:
    print("That's not a valid number!")
```

---

## 6. Escape Characters

```python
# Common escape characters
print("Line 1\nLine 2")       # Newline
print("Tab\there")             # Tab
print("She said \"hello\"")   # Escaped quotes
print('It\'s fine')            # Escaped apostrophe
print("Path: C:\\Users\\AI")   # Escaped backslash

# Raw strings (ignore escapes) — useful for file paths & regex
print(r"C:\Users\new\test")   # Prints literally
```

---

## 7. Practical: Building Prompts Programmatically

This is directly relevant to AI agent work — constructing prompts from templates:

```python
# System prompt template
def build_system_prompt(role, expertise, constraints):
    return f"""You are a {role} with expertise in {expertise}.

Rules:
- Always be helpful and accurate
- {constraints}
- If unsure, say "I don't know"
"""

# User prompt template  
def build_user_prompt(context, question):
    return f"""Context: {context}

Question: {question}

Please provide a detailed answer based on the context above."""

# Building a complete prompt
system = build_system_prompt(
    role="DevOps assistant",
    expertise="Kubernetes, Docker, and CI/CD pipelines",
    constraints="Keep answers concise and provide code examples"
)

user = build_user_prompt(
    context="We are running a 3-node K8s cluster on AWS EKS.",
    question="How do I set up horizontal pod autoscaling?"
)

print("=== SYSTEM PROMPT ===")
print(system)
print("=== USER PROMPT ===")
print(user)
```

---

## 8. Exercises

### Exercise 1: String Inspector
```python
# Given the string below, write code to:
text = "  The future of AI Agents is Autonomous Decision Making  "
# 1. Print the string stripped of whitespace
# 2. Print it in all uppercase  
# 3. Print how many times "A" appears (case-insensitive — count both 'a' and 'A')
# 4. Replace "Autonomous" with "Intelligent"
# 5. Split into a list of words
# 6. Print the 5th word (0-indexed)
# 7. Print the string reversed
```

### Exercise 2: Interactive AI Model Card
```python
# Build a program that:
# 1. Asks the user for: model name, version, parameter count, top use case
# 2. Prints a nicely formatted "Model Card" like:
#
# ╔══════════════════════════════╗
# ║       AI MODEL CARD          ║
# ╠══════════════════════════════╣
# ║ Name:       GPT-4            ║
# ║ Version:    4.0               ║
# ║ Parameters: 1,760,000,000    ║
# ║ Use Case:   Code Generation  ║
# ╚══════════════════════════════╝
```

### Exercise 3: Prompt Builder
```python
# Create a program that:
# 1. Asks the user for a "role" (e.g., "Python tutor")
# 2. Asks for a "topic" (e.g., "list comprehensions")
# 3. Asks for "difficulty" (beginner/intermediate/advanced)
# 4. Constructs and prints a well-structured prompt like:
#    "You are a Python tutor. Explain list comprehensions 
#     at a beginner level. Use simple examples and avoid jargon."
```

---

## Solutions

See [solutions/day02_solutions.py](../solutions/day02_solutions.py)

---

## Key Takeaways
- Strings are immutable sequences of characters
- Use slicing `[start:end:step]` to extract substrings
- Key methods: `.strip()`, `.split()`, `.join()`, `.replace()`, `.find()`
- `f-strings` are the best way to format output
- `input()` always returns a string — cast with `int()` or `float()` as needed
- Building prompts from templates is a core AI agent skill

**Tomorrow:** Conditionals and boolean logic →
