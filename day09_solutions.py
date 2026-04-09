# ============================================
# Day 9 Solutions — Error Handling
# ============================================

import json
from pathlib import Path


# --- Exercise 1: Robust API Response Parser ---
print("--- Robust API Response Parser ---")


def parse_api_response(raw_response: str) -> dict:
    """Parse an API response string, handling all errors gracefully."""
    try:
        data = json.loads(raw_response)
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON: {e}", "data": None}
    except TypeError:
        return {"error": "Response must be a string", "data": None}

    if not isinstance(data, dict):
        return {"error": "Expected a JSON object", "data": None}

    if "error" in data:
        return {"error": f"API error: {data['error']}", "data": None}

    try:
        content = data["choices"][0]["message"]["content"]
        tokens = data.get("usage", {}).get("total_tokens", 0)
        return {"data": content, "tokens": tokens, "error": None}
    except (KeyError, IndexError, TypeError) as e:
        return {"error": f"Missing expected field: {e}", "data": None}


# Test cases
test_responses = [
    '{"choices": [{"message": {"content": "Hello!"}}], "usage": {"total_tokens": 50}}',
    'not json at all',
    '{"error": "rate_limit_exceeded"}',
    '{"choices": []}',
    '42',
    None,
    '{"choices": [{"message": {}}]}',
]

for resp in test_responses:
    result = parse_api_response(resp)
    display = str(resp)[:50] if resp else str(resp)
    print(f"  Input: {display}")
    if result["error"]:
        print(f"    ❌ {result['error']}")
    else:
        print(f"    ✅ {result['data'][:40]}... ({result['tokens']} tokens)")
    print()


# --- Exercise 2: Safe File Operations ---
print("--- Safe File Operations ---")


def safe_read(filepath: str) -> str | None:
    """Read file with comprehensive error handling."""
    try:
        path = Path(filepath)
        if not path.exists():
            print(f"  Warning: File not found: {filepath}")
            return None
        if path.stat().st_size > 10 * 1024 * 1024:  # 10MB limit
            print(f"  Warning: File too large: {filepath}")
            return None
        return path.read_text(encoding="utf-8")
    except PermissionError:
        print(f"  Error: Permission denied: {filepath}")
        return None
    except UnicodeDecodeError:
        print(f"  Error: File is not valid UTF-8: {filepath}")
        return None
    except OSError as e:
        print(f"  Error reading file: {e}")
        return None


def safe_write(filepath: str, content: str) -> bool:
    """Write file with error handling."""
    try:
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"  ✅ Written: {filepath}")
        return True
    except PermissionError:
        print(f"  Error: Permission denied: {filepath}")
        return False
    except OSError as e:
        print(f"  Error writing file: {e}")
        return False


# Test
safe_write("test_output.txt", "Hello from safe_write!")
content = safe_read("test_output.txt")
print(f"  Read back: {content}")

safe_read("nonexistent_file.txt")

# Cleanup
Path("test_output.txt").unlink(missing_ok=True)


# --- Exercise 3: Custom Exception Hierarchy ---
print("\n--- Custom Exception Hierarchy ---")


class AgentError(Exception):
    """Base exception for agent operations."""
    pass


class ToolExecutionError(AgentError):
    """Raised when a tool fails to execute."""
    def __init__(self, tool_name: str, reason: str):
        self.tool_name = tool_name
        self.reason = reason
        super().__init__(f"Tool '{tool_name}' failed: {reason}")


class MemoryLimitError(AgentError):
    """Raised when agent memory exceeds limits."""
    def __init__(self, current: int, limit: int):
        self.current = current
        self.limit = limit
        super().__init__(f"Memory limit exceeded: {current}/{limit} tokens")


class RateLimitError(AgentError):
    """Raised when API rate limits are hit."""
    def __init__(self, retry_after: int = 60):
        self.retry_after = retry_after
        super().__init__(f"Rate limited. Retry after {retry_after}s")


def simulate_tool_call(tool_name: str, arg: str):
    """Simulate a tool call that might raise custom exceptions."""
    if tool_name == "search":
        raise ToolExecutionError(tool_name, f"Search API returned 503 for '{arg}'")
    if tool_name == "remember":
        raise MemoryLimitError(current=10000, limit=8000)
    if tool_name == "llm":
        raise RateLimitError(retry_after=30)
    return f"Tool '{tool_name}' executed successfully with arg '{arg}'"


# Test
test_calls = [
    ("search", "Python tutorials"),
    ("remember", "user prefers dark mode"),
    ("llm", "Hello"),
    ("calculator", "2+2"),
]

for tool, arg in test_calls:
    try:
        result = simulate_tool_call(tool, arg)
        print(f"  ✅ {result}")
    except ToolExecutionError as e:
        print(f"  🔧 ToolError: {e}")
    except MemoryLimitError as e:
        print(f"  🧠 MemoryError: {e} ({e.current - e.limit} over)")
    except RateLimitError as e:
        print(f"  ⏳ RateLimit: {e}")
    except AgentError as e:
        print(f"  ❌ AgentError: {e}")
