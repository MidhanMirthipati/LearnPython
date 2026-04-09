# Day 5: Functions & Scope

## Learning Goals
- Define and call functions
- Use parameters, defaults, and return values
- Understand variable scope (local vs global)
- Write reusable utilities for AI workflows

---

## 1. Defining Functions

```python
# Basic function
def greet():
    print("Hello from the AI Agent!")

greet()  # Call the function

# Function with parameters
def greet_user(name):
    print(f"Hello, {name}!")

greet_user("Alice")
greet_user("Bob")

# Function with return value
def add(a, b):
    return a + b

result = add(3, 5)
print(result)  # 8
```

---

## 2. Parameters & Arguments

```python
# Positional arguments
def create_prompt(role, task):
    return f"You are a {role}. Your task is to {task}."

prompt = create_prompt("DevOps engineer", "write Dockerfiles")
print(prompt)

# Keyword arguments (order doesn't matter)
prompt = create_prompt(task="review code", role="senior developer")
print(prompt)

# Default parameters
def call_llm(prompt, model="gpt-4o-mini", temperature=0.7, max_tokens=1000):
    print(f"Calling {model} with temp={temperature}, max_tokens={max_tokens}")
    print(f"Prompt: {prompt[:50]}...")

# Using defaults
call_llm("Explain Docker")

# Overriding specific defaults
call_llm("Write code", model="gpt-4", temperature=0.2)
```

---

## 3. Multiple Return Values

```python
def analyze_text(text):
    word_count = len(text.split())
    char_count = len(text)
    avg_word_length = char_count / word_count if word_count > 0 else 0
    return word_count, char_count, round(avg_word_length, 1)

words, chars, avg = analyze_text("AI agents can use tools to complete tasks")
print(f"Words: {words}, Chars: {chars}, Avg word length: {avg}")

# Returning a dict for clarity
def analyze_text_v2(text):
    words = text.split()
    return {
        "word_count": len(words),
        "char_count": len(text),
        "unique_words": len(set(words)),
        "avg_word_length": round(sum(len(w) for w in words) / len(words), 1) if words else 0
    }

stats = analyze_text_v2("the quick brown fox jumps over the lazy dog")
print(stats)
```

---

## 4. *args and **kwargs

```python
# *args — accept any number of positional arguments
def log_messages(*messages):
    for i, msg in enumerate(messages, 1):
        print(f"[{i}] {msg}")

log_messages("Starting agent", "Loading tools", "Ready")

# **kwargs — accept any number of keyword arguments
def create_agent(**config):
    print("Creating agent with config:")
    for key, value in config.items():
        print(f"  {key}: {value}")

create_agent(name="DevBot", model="gpt-4", temperature=0.3, tools=["search", "code"])

# Combining both
def agent_call(prompt, *examples, **settings):
    print(f"Prompt: {prompt}")
    if examples:
        print(f"Examples: {examples}")
    for k, v in settings.items():
        print(f"  {k}={v}")

agent_call("Translate this", "Hello→Hola", "Bye→Adiós", model="gpt-4", lang="Spanish")
```

---

## 5. Variable Scope

```python
# Global scope
model_name = "gpt-4"  # This is global

def get_model():
    # Local scope — can READ global variables
    print(f"Using model: {model_name}")

get_model()

# Local variables don't affect global
def set_temperature():
    temperature = 0.5  # This is LOCAL to this function
    print(f"Inside function: {temperature}")

set_temperature()
# print(temperature)  # ❌ NameError — temperature doesn't exist here

# Modifying global (avoid this if possible)
counter = 0

def increment():
    global counter
    counter += 1

increment()
increment()
print(counter)  # 2

# Better pattern: pass and return
def increment_value(current):
    return current + 1

counter = 0
counter = increment_value(counter)
counter = increment_value(counter)
print(counter)  # 2
```

---

## 6. Functions as First-Class Objects

```python
# Functions can be assigned to variables
def shout(text):
    return text.upper()

def whisper(text):
    return text.lower()

# Choose function based on condition
formatter = shout if True else whisper
print(formatter("hello"))  # HELLO

# Functions can be passed as arguments
def process_message(message, transform_func):
    return transform_func(message)

print(process_message("Hello Agent", shout))    # HELLO AGENT
print(process_message("Hello Agent", whisper))  # hello agent

# Storing functions in a data structure
tools = {
    "uppercase": shout,
    "lowercase": whisper,
    "length": len,
}

text = "AI Agent"
for name, func in tools.items():
    print(f"{name}: {func(text)}")
```

---

## 7. Type Hints (Annotations)

```python
# Type hints make your code self-documenting
def calculate_cost(tokens: int, cost_per_token: float) -> float:
    return tokens * cost_per_token

def build_prompt(role: str, task: str, examples: list[str] | None = None) -> str:
    prompt = f"You are a {role}. {task}"
    if examples:
        prompt += "\nExamples:\n"
        for ex in examples:
            prompt += f"- {ex}\n"
    return prompt

# Type hints are NOT enforced — they're documentation
result: float = calculate_cost(5000, 0.00003)
print(f"Cost: ${result:.4f}")
```

---

## 8. Practical: Building an Agent Tool Registry

```python
def search_web(query: str) -> str:
    """Simulate a web search tool."""
    return f"[Search results for '{query}': 5 results found]"

def calculate(expression: str) -> str:
    """Safely evaluate a math expression."""
    try:
        result = eval(expression, {"__builtins__": {}})
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {e}"

def get_time() -> str:
    """Get the current time."""
    from datetime import datetime
    return f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

# Tool registry
TOOLS = {
    "search": {
        "function": search_web,
        "description": "Search the web for information",
        "requires_input": True,
    },
    "calculate": {
        "function": calculate,
        "description": "Evaluate a math expression",
        "requires_input": True,
    },
    "time": {
        "function": get_time,
        "description": "Get the current date and time",
        "requires_input": False,
    },
}

def execute_tool(tool_name: str, tool_input: str = "") -> str:
    """Execute a registered tool by name."""
    if tool_name not in TOOLS:
        return f"Unknown tool: {tool_name}"
    
    tool = TOOLS[tool_name]
    if tool["requires_input"] and not tool_input:
        return f"Tool '{tool_name}' requires input"
    
    if tool["requires_input"]:
        return tool["function"](tool_input)
    else:
        return tool["function"]()

def list_tools() -> None:
    """Print all available tools."""
    print("Available Tools:")
    print("-" * 40)
    for name, info in TOOLS.items():
        print(f"  {name}: {info['description']}")

# Demo
list_tools()
print()
print(execute_tool("search", "Python AI agents"))
print(execute_tool("calculate", "2 ** 10"))
print(execute_tool("time"))
print(execute_tool("unknown_tool"))
```

---

## 9. Exercises

### Exercise 1: Token Estimator Suite
```python
# Build a set of functions:
# 1. estimate_tokens(text) — estimates tokens (~4 chars per token)
# 2. calculate_cost(tokens, model) — returns cost based on model:
#    - "gpt-4": $0.03/1K tokens
#    - "gpt-3.5": $0.002/1K tokens  
#    - "claude": $0.015/1K tokens
# 3. format_cost(cost) — returns string like "$0.0450"
# 4. analyze_prompt(text, model="gpt-3.5") — uses all above functions
#    to return a dict with: text_length, estimated_tokens, model, cost
# Test with several prompts of different lengths
```

### Exercise 2: Prompt Template Engine
```python
# Build a function-based prompt template engine:
# 1. create_template(name, template_string) — stores a template
# 2. list_templates() — prints all template names
# 3. render_template(name, **variables) — fills in {variable} placeholders
# 4. Store templates in a module-level dict
#
# Example usage:
# create_template("qa", "Context: {context}\nQuestion: {question}\nAnswer:")
# result = render_template("qa", context="Python is a language", question="What is Python?")
```

### Exercise 3: Function Dispatcher
```python
# Build a command dispatcher:
# 1. Create 5 functions: greet, farewell, help_menu, version, status
# 2. Store them in a dict mapping command strings to functions
# 3. Write a main loop that:
#    a. Asks user for a command
#    b. Looks up and executes the function
#    c. Prints "Unknown command" if not found
#    d. Exits on "quit"
```

---

## Solutions

See [solutions/day05_solutions.py](../solutions/day05_solutions.py)

---

## Key Takeaways
- Functions are defined with `def name(params):` and called with `name(args)`
- Use default parameters for optional settings
- Return multiple values as tuples, or return dicts for clarity
- `*args` and `**kwargs` accept variable numbers of arguments
- Variables have local scope inside functions; avoid `global`
- Functions are first-class: store them in dicts, pass them as arguments
- Type hints (`def f(x: int) -> str:`) document expected types

**Tomorrow:** Lists, tuples, and dictionaries in depth →
