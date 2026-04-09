# Day 1: Setup, Variables & Data Types

## Learning Goals
- Install Python and VS Code
- Run your first Python program
- Understand variables and basic data types
- Perform arithmetic operations

---

## 1. Setting Up Your Environment

### Install Python
1. Go to [python.org/downloads](https://www.python.org/downloads/)
2. Download Python 3.10 or newer
3. **IMPORTANT:** Check ✅ "Add Python to PATH" during installation
4. Open a terminal and verify:

```bash
python --version
# Should print: Python 3.10.x or newer
```

### Install VS Code
1. Download from [code.visualstudio.com](https://code.visualstudio.com/)
2. Install the **Python extension** (by Microsoft)
3. Create a folder for your course work: `C:\Users\YourName\python-ai-course\practice`

### Your First Program
Create a file called `hello.py`:

```python
print("Hello, World!")
print("I am learning Python for AI Agents!")
```

Run it:
```bash
python hello.py
```

---

## 2. Variables

A **variable** is a name that stores a value. Think of it like a labeled box.

```python
# Creating variables
name = "Alice"
age = 30
temperature = 98.6
is_active = True

# Using variables
print(name)
print(age)
print(temperature)
print(is_active)
```

### Variable Naming Rules
```python
# ✅ Valid names
user_name = "Bob"
age2 = 25
_private = "secret"
MAX_RETRIES = 3

# ❌ Invalid names
# 2fast = "no"        # Can't start with a number
# my-name = "no"      # No hyphens
# class = "no"        # Can't use reserved words
```

### Python Naming Convention
```python
# Use snake_case for variables and functions
user_name = "Alice"
max_retry_count = 5

# Use UPPER_CASE for constants
API_KEY = "abc123"
MAX_TOKENS = 4096
```

---

## 3. Data Types

Python has several built-in data types. These four are fundamental:

| Type | Example | Description |
|------|---------|-------------|
| `int` | `42` | Whole numbers |
| `float` | `3.14` | Decimal numbers |
| `str` | `"hello"` | Text (strings) |
| `bool` | `True` / `False` | Boolean values |

```python
# Checking types with type()
x = 42
print(type(x))        # <class 'int'>

y = 3.14
print(type(y))        # <class 'float'>

name = "Agent"
print(type(name))     # <class 'str'>

active = True
print(type(active))   # <class 'bool'>
```

### Type Conversion
```python
# String to int
age_str = "25"
age_int = int(age_str)
print(age_int + 5)    # 30

# Int to string
count = 10
message = "There are " + str(count) + " items"
print(message)

# String to float
price = float("19.99")
print(price)           # 19.99

# Float to int (truncates, does NOT round)
score = int(9.8)
print(score)           # 9
```

---

## 4. Arithmetic Operations

```python
a = 15
b = 4

print(a + b)    # 19    Addition
print(a - b)    # 11    Subtraction
print(a * b)    # 60    Multiplication
print(a / b)    # 3.75  Division (always returns float)
print(a // b)   # 3     Floor division (integer result)
print(a % b)    # 3     Modulus (remainder)
print(a ** b)   # 50625 Exponentiation (15^4)
```

### Assignment Operators
```python
tokens = 100
tokens += 10    # tokens = tokens + 10 → 110
tokens -= 5     # tokens = tokens - 5  → 105
tokens *= 2     # tokens = tokens * 2  → 210
tokens //= 3    # tokens = tokens // 3 → 70

print(tokens)   # 70
```

---

## 5. f-Strings (Formatted Strings)

The modern way to embed variables in strings:

```python
name = "GPT Agent"
version = 4
accuracy = 95.7

# f-string syntax: f"text {variable}"
print(f"Agent: {name}")
print(f"Version: {version}")
print(f"Accuracy: {accuracy}%")

# Expressions inside f-strings
price = 29.99
quantity = 3
print(f"Total: ${price * quantity:.2f}")  # Total: $89.97

# Multi-line f-strings
summary = f"""
Agent Report
============
Name:     {name}
Version:  {version}
Accuracy: {accuracy}%
"""
print(summary)
```

---

## 6. Exercises

### Exercise 1: Variable Practice
Create variables for an AI model's properties and print a formatted summary.

```python
# Create these variables:
# model_name  → "gpt-4o-mini"  (or "claude-sonnet-4-20250514" or "gemini-2.0-flash")
# parameters  → 1760000000000  (1.76 trillion)
# context_window → 128000
# is_multimodal → True
# cost_per_token → 0.00003

# Print a formatted summary using f-strings like:
# Model: gpt-4o-mini
# Parameters: 1760000000000
# Context Window: 128000 tokens
# Multimodal: True
# Cost: $0.00003 per token
```

### Exercise 2: Token Cost Calculator
```python
# Write a program that:
# 1. Stores the number of input tokens (e.g., 5000)
# 2. Stores the number of output tokens (e.g., 2000)
# 3. Stores cost per input token ($0.00003)
# 4. Stores cost per output token ($0.00006)
# 5. Calculates total cost
# 6. Prints: "Input cost: $X.XX"
# 7. Prints: "Output cost: $X.XX"
# 8. Prints: "Total cost: $X.XX"
```

### Exercise 3: Type Detective
```python
# For each value below, predict the type, then verify with type()
# a) 42
# b) 42.0
# c) "42"
# d) True
# e) 3 + 4.0    (what type is the result?)
# f) 10 / 2     (what type is the result?)
# g) 10 // 2    (what type is the result?)
```

---

## Solutions

See [solutions/day01_solutions.py](../solutions/day01_solutions.py)

---

## Key Takeaways
- Variables store values with descriptive names (`snake_case`)
- Four basic types: `int`, `float`, `str`, `bool`
- Use `type()` to check a value's type
- Use `int()`, `float()`, `str()` to convert between types
- f-strings (`f"text {var}"`) are the cleanest way to format output
- Python uses `**` for exponents, `//` for floor division, `%` for remainder

**Tomorrow:** Strings in depth, user input, and output formatting →
