# Day 8: File I/O & JSON

## Learning Goals
- Read and write text files
- Work with JSON data (the lingua franca of APIs)
- Handle YAML configuration files
- Build a persistent data store

---

## 1. Reading Files

```python
# Method 1: read() — entire file as one string
with open("example.txt", "r") as f:
    content = f.read()
    print(content)

# Method 2: readlines() — list of lines
with open("example.txt", "r") as f:
    lines = f.readlines()
    for line in lines:
        print(line.strip())  # strip() removes trailing \n

# Method 3: iterate line by line (memory-efficient for large files)
with open("example.txt", "r") as f:
    for line in f:
        print(line.strip())
```

### The `with` Statement
```python
# 'with' automatically closes the file when done — ALWAYS use it
# ✅ Good
with open("file.txt", "r") as f:
    data = f.read()

# ❌ Bad — you might forget to close
f = open("file.txt", "r")
data = f.read()
f.close()  # Easy to forget, especially if an error occurs
```

---

## 2. Writing Files

```python
# Write (creates or overwrites)
with open("output.txt", "w") as f:
    f.write("Line 1\n")
    f.write("Line 2\n")

# Append (adds to existing file)
with open("output.txt", "a") as f:
    f.write("Line 3 (appended)\n")

# Write multiple lines
lines = ["Agent log entry 1", "Agent log entry 2", "Agent log entry 3"]
with open("log.txt", "w") as f:
    for line in lines:
        f.write(line + "\n")

# Or use writelines (does NOT add newlines automatically)
with open("log.txt", "w") as f:
    f.writelines(line + "\n" for line in lines)
```

---

## 3. File Modes

| Mode | Description |
|------|-------------|
| `"r"` | Read (default). File must exist. |
| `"w"` | Write. Creates or **overwrites** file. |
| `"a"` | Append. Creates if doesn't exist. |
| `"x"` | Exclusive create. Fails if file exists. |
| `"r+"` | Read and write. File must exist. |
| `"b"` | Binary mode (add to above, e.g., `"rb"`). |

---

## 4. Working with JSON

JSON is the standard format for API requests/responses in AI.

```python
import json

# Python dict → JSON string
agent_config = {
    "name": "DevOps Agent",
    "model": "gpt-4",
    "temperature": 0.7,
    "tools": ["search", "code_exec", "deploy"],
    "metadata": {
        "version": "2.0",
        "author": "Team AI"
    }
}

# Convert to JSON string
json_string = json.dumps(agent_config, indent=2)
print(json_string)

# JSON string → Python dict
parsed = json.loads(json_string)
print(parsed["name"])  # "DevOps Agent"

# Write JSON to file
with open("agent_config.json", "w") as f:
    json.dump(agent_config, f, indent=2)

# Read JSON from file
with open("agent_config.json", "r") as f:
    loaded_config = json.load(f)
    print(loaded_config["model"])
```

### JSON Type Mapping

| Python | JSON |
|--------|------|
| `dict` | `object {}` |
| `list` | `array []` |
| `str` | `string` |
| `int/float` | `number` |
| `True/False` | `true/false` |
| `None` | `null` |

---

## 5. Working with Paths (pathlib)

```python
from pathlib import Path

# Create paths
config_dir = Path("config")
config_file = config_dir / "settings.json"

# Check existence
print(config_file.exists())

# Create directories
config_dir.mkdir(exist_ok=True)  # Won't error if already exists

# Read/write with pathlib
config_file.write_text('{"model": "gpt-4"}')
content = config_file.read_text()
print(content)

# Useful path operations
print(config_file.name)       # "settings.json"
print(config_file.stem)       # "settings"
print(config_file.suffix)     # ".json"
print(config_file.parent)     # "config"

# List files in a directory
for file in Path(".").glob("*.py"):
    print(file)

# Recursive search
for file in Path(".").rglob("*.json"):
    print(file)
```

---

## 6. CSV Files

```python
import csv

# Writing CSV
data = [
    ["model", "score", "cost"],
    ["GPT-4", "92.5", "0.03"],
    ["Claude", "91.8", "0.015"],
    ["Gemini", "90.3", "0.001"],
]

with open("models.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(data)

# Reading CSV
with open("models.csv", "r") as f:
    reader = csv.reader(f)
    header = next(reader)  # Skip header
    for row in reader:
        print(f"{row[0]}: Score={row[1]}, Cost=${row[2]}")

# DictReader (access by column name)
with open("models.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(f"{row['model']}: {row['score']}")
```

---

## 7. Practical: Conversation Persistence

```python
import json
from pathlib import Path
from datetime import datetime

HISTORY_DIR = Path("conversations")
HISTORY_DIR.mkdir(exist_ok=True)

def save_conversation(messages: list[dict], session_id: str) -> str:
    """Save conversation history to a JSON file."""
    filepath = HISTORY_DIR / f"{session_id}.json"
    data = {
        "session_id": session_id,
        "saved_at": datetime.now().isoformat(),
        "message_count": len(messages),
        "messages": messages
    }
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
    return str(filepath)

def load_conversation(session_id: str) -> list[dict]:
    """Load a conversation from file."""
    filepath = HISTORY_DIR / f"{session_id}.json"
    if not filepath.exists():
        print(f"No conversation found for session: {session_id}")
        return []
    
    with open(filepath, "r") as f:
        data = json.load(f)
    
    print(f"Loaded {data['message_count']} messages from {data['saved_at']}")
    return data["messages"]

def list_conversations() -> list[str]:
    """List all saved conversations."""
    files = list(HISTORY_DIR.glob("*.json"))
    sessions = []
    for f in files:
        with open(f) as fh:
            data = json.load(fh)
        sessions.append({
            "session_id": data["session_id"],
            "messages": data["message_count"],
            "saved_at": data["saved_at"]
        })
    return sessions

# Demo
messages = [
    {"role": "system", "content": "You are a DevOps assistant."},
    {"role": "user", "content": "How do I set up CI/CD?"},
    {"role": "assistant", "content": "Here are the steps for CI/CD..."}
]

save_conversation(messages, "session_001")
loaded = load_conversation("session_001")
print(loaded)
```

---

## 8. Exercises

### Exercise 1: Log File Analyzer
```python
# Create a file called "agent_log.txt" with these lines:
# [INFO] Agent started
# [ERROR] API call failed: timeout
# [INFO] Retrying...
# [INFO] API call successful
# [WARNING] Token usage at 80%
# [ERROR] Rate limit exceeded
# [INFO] Waiting 60 seconds
# [INFO] Resumed operations
#
# Write a program that:
# 1. Reads the log file
# 2. Counts messages by level (INFO, ERROR, WARNING)
# 3. Extracts and prints only ERROR messages
# 4. Writes a summary to "log_summary.json"
```

### Exercise 2: Config Manager
```python
# Build a configuration manager that:
# 1. Loads settings from a JSON file (or creates defaults if missing)
# 2. Allows updating individual settings
# 3. Saves changes back to the file
# 4. Has a reset function that restores defaults
# Default settings:
# {"model": "gpt-3.5-turbo", "temperature": 0.7, "max_tokens": 1000,
#  "system_prompt": "You are a helpful assistant.", "stream": false}
```

### Exercise 3: Chat Export/Import
```python
# 1. Build on the ConversationManager from Day 6
# 2. Add export_to_json(filepath) method
# 3. Add a class method load_from_json(filepath) that creates a new ConversationManager
# 4. Add export_to_markdown(filepath) that creates a readable markdown file
# 5. Test: create a conversation, export it, load it, verify it matches
```

---

## Solutions

See [solutions/day08_solutions.py](../solutions/day08_solutions.py)

---

## Key Takeaways
- Always use `with open(...)` for file operations (auto-closes)
- `json.dump()`/`json.load()` for files; `json.dumps()`/`json.loads()` for strings
- `pathlib.Path` is modern and cleaner than `os.path`
- JSON is the standard data format for AI APIs
- Saving conversation history to files enables persistence across sessions

**Tomorrow:** Error handling and debugging →
