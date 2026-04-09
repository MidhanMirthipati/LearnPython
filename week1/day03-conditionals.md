# Day 3: Conditionals & Boolean Logic

## Learning Goals
- Use `if`, `elif`, `else` to control program flow
- Understand comparison and logical operators
- Write nested conditions
- Build a decision-making program

---

## 1. Comparison Operators

```python
a = 10
b = 20

print(a == b)   # False  — equal to
print(a != b)   # True   — not equal to
print(a < b)    # True   — less than
print(a > b)    # False  — greater than
print(a <= b)   # True   — less than or equal
print(a >= 10)  # True   — greater than or equal

# Strings can be compared too
print("apple" == "apple")  # True
print("apple" < "banana")  # True (alphabetical order)
```

---

## 2. if / elif / else

```python
temperature = 35

if temperature > 30:
    print("It's hot outside! 🔥")
elif temperature > 20:
    print("Nice weather! ☀️")
elif temperature > 10:
    print("A bit chilly. 🧥")
else:
    print("It's cold! ❄️")
```

### Important Rules
```python
# 1. Indentation matters (use 4 spaces)
if True:
    print("This is inside the if")
print("This is outside the if")

# 2. elif and else are optional
age = 25
if age >= 18:
    print("Adult")

# 3. Only the FIRST matching branch executes
score = 95
if score >= 90:
    print("A")    # This prints
elif score >= 80:
    print("B")    # This is SKIPPED even though 95 >= 80
```

---

## 3. Logical Operators

```python
age = 25
has_license = True
is_insured = False

# and — both must be True
if age >= 18 and has_license:
    print("Can drive")

# or — at least one must be True
if has_license or is_insured:
    print("Has some documentation")

# not — inverts the value
if not is_insured:
    print("Needs insurance!")

# Combining operators
if age >= 18 and has_license and not is_insured:
    print("Can drive but needs insurance")
```

### Truthiness and Falsiness

```python
# These are all "falsy" in Python:
# False, 0, 0.0, "", [], {}, None

# These are all "truthy":
# True, any non-zero number, any non-empty string/list/dict

name = ""
if name:
    print(f"Hello, {name}")
else:
    print("Name is empty!")  # This prints

tokens = 0
if tokens:
    print("Has tokens")
else:
    print("No tokens left!")  # This prints

# Useful for checking if a variable has a meaningful value
api_key = None
if not api_key:
    print("Warning: No API key set!")
```

---

## 4. Nested Conditionals

```python
user_role = "admin"
is_authenticated = True
has_2fa = True

if is_authenticated:
    if user_role == "admin":
        if has_2fa:
            print("Full admin access granted")
        else:
            print("Admin access requires 2FA")
    elif user_role == "editor":
        print("Editor access granted")
    else:
        print("Viewer access granted")
else:
    print("Please log in first")
```

### Prefer flat over nested (Pythonic style)
```python
# Better: Use early returns or combined conditions
def check_access(is_authenticated, user_role, has_2fa):
    if not is_authenticated:
        return "Please log in first"
    
    if user_role == "admin" and not has_2fa:
        return "Admin access requires 2FA"
    
    if user_role == "admin" and has_2fa:
        return "Full admin access granted"
    
    if user_role == "editor":
        return "Editor access granted"
    
    return "Viewer access granted"
```

---

## 5. The `in` Operator

```python
# Check membership in a collection
allowed_models = ["gpt-4o-mini", "gpt-4o", "claude-sonnet-4-20250514", "claude-haiku-4-20250514", "gemini-2.0-flash", "gemini-2.5-pro"]

user_model = "gpt-4o-mini"
if user_model in allowed_models:
    print(f"Using model: {user_model}")
else:
    print(f"Model '{user_model}' is not available")

# Works with strings too
response = "Error: rate limit exceeded"
if "error" in response.lower():
    print("An error occurred!")
```

---

## 6. Ternary (Conditional) Expressions

```python
# One-liner conditionals
age = 20
status = "adult" if age >= 18 else "minor"
print(status)  # "adult"

# Useful for setting defaults
api_key = None
key_to_use = api_key if api_key else "default-key"

# In f-strings
tokens_used = 150
max_tokens = 100
print(f"Status: {'OVER LIMIT' if tokens_used > max_tokens else 'OK'}")
```

---

## 7. Match/Case (Python 3.10+)

```python
# Structural pattern matching — like a powerful switch statement
def handle_agent_action(action):
    match action:
        case "search":
            return "Searching the web..."
        case "calculate":
            return "Running calculation..."
        case "summarize":
            return "Generating summary..."
        case "code":
            return "Writing code..."
        case _:
            return f"Unknown action: {action}"

print(handle_agent_action("search"))
print(handle_agent_action("dance"))
```

---

## 8. Practical: AI Model Router

A real-world example — routing requests to different AI models based on criteria:

```python
def route_request(task_type, budget, needs_vision=False):
    """Route an AI request to the best model across providers."""
    
    if needs_vision:
        if budget == "high":
            model = "gpt-4o"           # OpenAI vision
        else:
            model = "gemini-2.0-flash"  # Gemini (free tier available)
        return f"Vision task → {model}"
    
    if task_type == "code":
        if budget == "high":
            return "Code task → claude-sonnet-4-20250514"  # Anthropic
        else:
            return "Code task → gpt-4o-mini"        # OpenAI
    
    if task_type == "chat":
        return "Chat task → gemini-2.0-flash"       # Google (free tier)
    
    if task_type == "analysis":
        if budget == "high":
            return "Analysis → claude-sonnet-4-20250514"   # Anthropic
        else:
            return "Analysis → gpt-4o-mini"         # OpenAI
    
    return f"Unknown task type: {task_type}"

# Test the router
print(route_request("code", "high"))
print(route_request("chat", "low"))
print(route_request("analysis", "high"))
print(route_request("code", "low", needs_vision=True))
```

---

## 9. Exercises

### Exercise 1: Token Budget Checker
```python
# Write a program that:
# 1. Asks for the total token budget (int)
# 2. Asks for tokens already used (int)
# 3. Calculates remaining tokens
# 4. Prints a status:
#    - If > 75% budget remains: "Budget healthy ✅"
#    - If 25-75% remains: "Budget moderate ⚠️"
#    - If < 25% remains: "Budget critical 🚨"
#    - If 0 or negative: "Budget exhausted! ❌"
# 5. Print the percentage remaining
```

### Exercise 2: API Key Validator
```python
# Write a function that validates an API key:
# - Must start with "sk-"
# - Must be at least 20 characters long
# - Must not contain spaces
# - Must contain at least one digit
# Return "Valid" or a specific error message explaining what's wrong
```

### Exercise 3: Agent Action Classifier
```python
# Write a function that takes a user message (string) and classifies it:
# - If it contains "weather" or "temperature" → "weather_tool"
# - If it contains "calculate" or "math" or any digit → "calculator_tool"
# - If it contains "search" or "find" or "look up" → "search_tool"
# - If it contains "remember" or "save" or "note" → "memory_tool"
# - Otherwise → "general_chat"
# Test with at least 5 different inputs
```

---

## Solutions

See [solutions/day03_solutions.py](../solutions/day03_solutions.py)

---

## Key Takeaways
- `if/elif/else` controls program flow based on conditions
- Comparison: `==`, `!=`, `<`, `>`, `<=`, `>=`
- Logical: `and`, `or`, `not`
- `in` checks membership in lists and strings
- Falsy values: `False`, `0`, `""`, `[]`, `{}`, `None`
- Ternary: `value_if_true if condition else value_if_false`
- Keep conditions flat and readable — avoid deep nesting

**Tomorrow:** Loops and iteration →
