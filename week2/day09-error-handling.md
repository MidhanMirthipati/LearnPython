# Day 9: Error Handling & Debugging

## Learning Goals
- Use try/except to handle errors gracefully
- Understand common exception types
- Raise custom exceptions
- Debug effectively with print and logging

---

## 1. Why Error Handling Matters

In AI agent work, errors happen constantly:
- API rate limits, timeouts, invalid responses
- Malformed JSON from LLM output
- File not found, permission denied
- Network failures

Without error handling, your agent crashes. With it, your agent recovers gracefully.

---

## 2. try / except Basics

```python
# Without error handling — crashes on bad input
# number = int(input("Enter a number: "))  # Crashes if user types "abc"

# With error handling
try:
    number = int(input("Enter a number: "))
    print(f"Double: {number * 2}")
except ValueError:
    print("That's not a valid number!")
```

### Catching Specific Exceptions
```python
def safe_divide(a, b):
    try:
        result = a / b
        return result
    except ZeroDivisionError:
        print("Cannot divide by zero!")
        return None
    except TypeError:
        print("Both arguments must be numbers!")
        return None

print(safe_divide(10, 3))    # 3.333...
print(safe_divide(10, 0))    # Cannot divide by zero! → None
print(safe_divide("10", 3))  # Both arguments must be numbers! → None
```

### Accessing the Error Object
```python
try:
    data = {"name": "Agent"}
    print(data["model"])
except KeyError as e:
    print(f"Missing key: {e}")  # Missing key: 'model'

try:
    import nonexistent_module
except ImportError as e:
    print(f"Import error: {e}")
```

---

## 3. try / except / else / finally

```python
def load_config(filepath):
    try:
        with open(filepath, "r") as f:
            import json
            config = json.load(f)
    except FileNotFoundError:
        print(f"Config file not found: {filepath}")
        config = {}
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in {filepath}: {e}")
        config = {}
    else:
        # Runs ONLY if no exception occurred
        print(f"Config loaded successfully from {filepath}")
    finally:
        # Runs ALWAYS, no matter what
        print("Config loading attempt complete.")
    
    return config

config = load_config("settings.json")
```

---

## 4. Common Exception Types

| Exception | When It Occurs |
|-----------|----------------|
| `ValueError` | Wrong value type (`int("abc")`) |
| `TypeError` | Wrong type for operation (`"5" + 3`) |
| `KeyError` | Dict key doesn't exist |
| `IndexError` | List index out of range |
| `FileNotFoundError` | File doesn't exist |
| `ZeroDivisionError` | Division by zero |
| `AttributeError` | Object doesn't have that attribute |
| `ImportError` | Module not found |
| `ConnectionError` | Network connection fails |
| `TimeoutError` | Operation timed out |
| `json.JSONDecodeError` | Invalid JSON string |

---

## 5. Raising Exceptions

```python
def set_temperature(temp: float) -> float:
    if not isinstance(temp, (int, float)):
        raise TypeError(f"Temperature must be a number, got {type(temp)}")
    if temp < 0.0 or temp > 2.0:
        raise ValueError(f"Temperature must be 0.0-2.0, got {temp}")
    return temp

# Usage
try:
    t = set_temperature(0.7)
    print(f"Set to {t}")
    
    t = set_temperature(5.0)  # Raises ValueError
except ValueError as e:
    print(f"Invalid setting: {e}")
```

### Custom Exceptions
```python
class AgentError(Exception):
    """Base exception for agent errors."""
    pass

class ToolNotFoundError(AgentError):
    """Raised when a requested tool doesn't exist."""
    pass

class TokenBudgetExceeded(AgentError):
    """Raised when token usage exceeds budget."""
    def __init__(self, used, budget):
        self.used = used
        self.budget = budget
        super().__init__(f"Token budget exceeded: {used}/{budget}")

# Usage
def execute_tool(tool_name, tools_registry):
    if tool_name not in tools_registry:
        raise ToolNotFoundError(f"Tool '{tool_name}' is not registered")
    return tools_registry[tool_name]()

def check_tokens(used, budget):
    if used > budget:
        raise TokenBudgetExceeded(used, budget)

try:
    check_tokens(5000, 4000)
except TokenBudgetExceeded as e:
    print(f"Error: {e}")
    print(f"Used: {e.used}, Budget: {e.budget}")
```

---

## 6. The Logging Module

```python
import logging

# Basic setup
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger("agent")

# Log levels (from least to most severe)
logger.debug("Detailed info for debugging")
logger.info("General operational info")
logger.warning("Something unexpected but not critical")
logger.error("An error occurred")
logger.critical("System is in a critical state")

# Practical example
def call_api(prompt):
    logger.info(f"Calling API with prompt length: {len(prompt)}")
    try:
        # Simulate API call
        if len(prompt) > 10000:
            raise ValueError("Prompt too long")
        logger.debug("API call successful")
        return "API response here"
    except ValueError as e:
        logger.error(f"API call failed: {e}")
        return None

# Log to file
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("agent.log"),
        logging.StreamHandler()  # Also print to console
    ]
)
```

---

## 7. Practical: Resilient API Caller

```python
import time
import random
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("api_client")

class APIError(Exception):
    pass

class RateLimitError(APIError):
    def __init__(self, retry_after=60):
        self.retry_after = retry_after
        super().__init__(f"Rate limited. Retry after {retry_after}s")

def simulate_api_call(prompt: str) -> str:
    """Simulates an unreliable API call."""
    roll = random.random()
    if roll < 0.3:
        raise ConnectionError("Network timeout")
    elif roll < 0.5:
        raise RateLimitError(retry_after=random.randint(1, 5))
    elif roll < 0.6:
        raise APIError("Internal server error")
    return f"Response to: {prompt[:30]}..."

def resilient_call(prompt: str, max_retries: int = 3, base_delay: float = 1.0) -> str | None:
    """Call API with exponential backoff retry logic."""
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Attempt {attempt}/{max_retries}")
            result = simulate_api_call(prompt)
            logger.info("Success!")
            return result
        
        except RateLimitError as e:
            wait_time = e.retry_after
            logger.warning(f"Rate limited. Would wait {wait_time}s")
            # time.sleep(wait_time)  # In real code, you'd actually wait
        
        except ConnectionError as e:
            delay = base_delay * (2 ** (attempt - 1))  # Exponential backoff
            logger.warning(f"Connection failed: {e}. Would retry in {delay}s")
            # time.sleep(delay)
        
        except APIError as e:
            logger.error(f"API error: {e}. Not retrying.")
            return None
    
    logger.error("All retries exhausted")
    return None

# Test it
for i in range(5):
    print(f"\n--- Request {i+1} ---")
    result = resilient_call("Explain Kubernetes pod networking")
    print(f"Result: {result}")
```

---

## 8. Debugging Techniques

### Print Debugging (Quick & Dirty)
```python
def process_messages(messages):
    print(f"DEBUG: Input messages count = {len(messages)}")  # Debug
    
    filtered = [m for m in messages if m.get("role") != "system"]
    print(f"DEBUG: After filter = {len(filtered)}")  # Debug
    
    total_tokens = sum(len(m["content"].split()) for m in filtered)
    print(f"DEBUG: Total tokens = {total_tokens}")  # Debug
    
    return filtered, total_tokens
```

### Using Assertions
```python
def create_agent(name, model, temperature):
    assert isinstance(name, str) and len(name) > 0, "Name must be non-empty string"
    assert model in ["gpt-4", "gpt-3.5-turbo", "claude-3"], f"Invalid model: {model}"
    assert 0 <= temperature <= 2, f"Temperature out of range: {temperature}"
    
    return {"name": name, "model": model, "temperature": temperature}
```

### Using breakpoint() (Python 3.7+)
```python
def mysterious_bug(data):
    processed = [d.upper() for d in data if d]
    breakpoint()  # Drops into interactive debugger (pdb)
    return processed

# When you hit breakpoint(), you can:
# - Type variable names to inspect them
# - Type 'n' for next line
# - Type 'c' to continue
# - Type 'q' to quit
```

---

## 9. Exercises

### Exercise 1: Safe JSON Parser
```python
# Write a function safe_parse_json(text) that:
# 1. Tries to parse the text as JSON
# 2. If valid, returns the parsed data
# 3. If invalid JSON, tries to fix common issues:
#    - Strip leading/trailing whitespace
#    - Handle single quotes → double quotes
#    - Handle trailing commas
# 4. If still invalid, returns None and logs the error
# Test with: valid JSON, invalid JSON, edge cases
```

### Exercise 2: Resilient File Processor
```python
# Write a function that processes a directory of JSON config files:
# 1. List all .json files in a directory
# 2. Try to load each one
# 3. Skip files that are invalid JSON (log a warning)
# 4. Collect valid configs into a list
# 5. Return summary: {total_files, valid, invalid, errors: []}
```

### Exercise 3: Validated Agent Config
```python
# Create a function validate_agent_config(config: dict) that:
# 1. Checks required keys: name, model, temperature
# 2. Validates model is in allowed list
# 3. Validates temperature is 0.0-2.0
# 4. Validates max_tokens is positive int if provided
# 5. Returns (True, config) if valid
# 6. Returns (False, list_of_errors) if invalid
# Raise custom ValidationError with all collected errors
```

---

## Solutions

See [solutions/day09_solutions.py](../solutions/day09_solutions.py)

---

## Key Takeaways
- Always catch **specific** exceptions, not bare `except:`
- Use `try/except/else/finally` for complete error handling
- Build retry logic with exponential backoff for API calls
- Create custom exceptions for domain-specific errors
- Use `logging` instead of `print()` for production code
- `raise` to signal errors; `assert` for development-time checks

**Tomorrow:** Modules, packages & pip →
