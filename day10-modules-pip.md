# Day 10: Modules, Packages & pip

## Learning Goals
- Import and use standard library modules
- Create your own modules and packages
- Install third-party packages with pip
- Use virtual environments

---

## 1. Importing Modules

```python
# Import entire module
import math
print(math.sqrt(16))   # 4.0
print(math.pi)         # 3.14159...

# Import specific items
from math import sqrt, pi
print(sqrt(16))        # 4.0

# Import with alias
import json as j
data = j.dumps({"key": "value"})

# Import everything (avoid — pollutes namespace)
# from math import *
```

---

## 2. Useful Standard Library Modules

### os & sys
```python
import os
import sys

# Environment variables (crucial for API keys)
api_key = os.environ.get("OPENAI_API_KEY", "not-set")
print(f"API Key: {api_key[:8]}..." if api_key != "not-set" else "No key")

# Current directory
print(os.getcwd())

# Python version
print(sys.version)

# Command line arguments
print(sys.argv)  # ['script.py', 'arg1', 'arg2']
```

### datetime
```python
from datetime import datetime, timedelta

now = datetime.now()
print(now.strftime("%Y-%m-%d %H:%M:%S"))

# Timestamps for logging
timestamp = datetime.now().isoformat()
print(f"[{timestamp}] Agent started")

# Time math
tomorrow = now + timedelta(days=1)
one_hour_ago = now - timedelta(hours=1)
```

### random
```python
import random

# Random selection (useful for varied agent responses)
greetings = ["Hello!", "Hi there!", "Hey!", "Greetings!"]
print(random.choice(greetings))

# Random number
print(random.randint(1, 100))    # Random integer
print(random.random())           # Random float 0-1
print(random.uniform(0.0, 2.0))  # Random float in range

# Shuffle a list
items = [1, 2, 3, 4, 5]
random.shuffle(items)
print(items)
```

### collections
```python
from collections import Counter, defaultdict

# Counter — count occurrences
words = ["agent", "tool", "agent", "model", "tool", "agent"]
word_counts = Counter(words)
print(word_counts)                    # Counter({'agent': 3, 'tool': 2, 'model': 1})
print(word_counts.most_common(2))     # [('agent', 3), ('tool', 2)]

# defaultdict — dict with default values
tool_usage = defaultdict(int)
actions = ["search", "code", "search", "search", "code"]
for action in actions:
    tool_usage[action] += 1
print(dict(tool_usage))  # {'search': 3, 'code': 2}
```

### hashlib (for hashing)
```python
import hashlib

# Create a unique ID from content (useful for caching)
def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:12]

prompt = "Explain Docker containers"
cache_key = content_hash(prompt)
print(f"Cache key: {cache_key}")
```

---

## 3. Creating Your Own Modules

### File Structure
```
my_project/
├── main.py
├── utils.py
└── agent/
    ├── __init__.py
    ├── core.py
    └── tools.py
```

### utils.py
```python
"""Utility functions for the AI agent."""

def estimate_tokens(text: str) -> int:
    """Estimate token count (~4 chars per token)."""
    return len(text) // 4

def format_cost(cost: float) -> str:
    """Format a cost value as a dollar string."""
    return f"${cost:.6f}"

# This only runs when the file is executed directly, not when imported
if __name__ == "__main__":
    print(estimate_tokens("Hello, world!"))
    print(format_cost(0.00003))
```

### agent/core.py
```python
"""Core agent functionality."""

from datetime import datetime

class Agent:
    def __init__(self, name: str, model: str):
        self.name = name
        self.model = model
        self.created_at = datetime.now()
    
    def __repr__(self):
        return f"Agent(name='{self.name}', model='{self.model}')"
```

### agent/__init__.py
```python
"""Agent package."""
from .core import Agent
```

### main.py
```python
# Import from your own modules
from utils import estimate_tokens, format_cost
from agent import Agent

# Use them
tokens = estimate_tokens("How do I deploy to Kubernetes?")
cost = format_cost(tokens * 0.00003)
print(f"Tokens: {tokens}, Cost: {cost}")

bot = Agent("DevBot", "gpt-4")
print(bot)
```

---

## 4. pip & Package Management

```bash
# Install a package
pip install requests

# Install a specific version
pip install openai==1.12.0

# Install multiple packages
pip install requests python-dotenv langchain

# List installed packages
pip list

# Show package info
pip show openai

# Freeze current packages to requirements.txt
pip freeze > requirements.txt

# Install from requirements.txt
pip install -r requirements.txt

# Upgrade a package
pip install --upgrade openai

# Uninstall
pip uninstall requests
```

---

## 5. Virtual Environments

```bash
# Create a virtual environment
python -m venv ai-agent-env

# Activate (Windows)
ai-agent-env\Scripts\activate

# Activate (Linux/Mac)
source ai-agent-env/bin/activate

# Your prompt changes:
# (ai-agent-env) C:\Users\you\project>

# Install packages (isolated to this env)
pip install openai langchain

# Deactivate
deactivate
```

### Requirements File
```
# requirements.txt
openai>=1.12.0
requests>=2.31.0
python-dotenv>=1.0.0
langchain>=0.1.0
pandas>=2.0.0
chromadb>=0.4.0
```

---

## 6. Practical: Project Scaffolding Tool

```python
"""A script that creates a standard AI agent project structure."""

from pathlib import Path
import json

def create_project(project_name: str):
    """Create a new AI agent project with standard structure."""
    root = Path(project_name)
    
    # Define structure
    directories = [
        root / "agent",
        root / "tools",
        root / "config",
        root / "logs",
        root / "data",
        root / "tests",
    ]
    
    # Create directories
    for d in directories:
        d.mkdir(parents=True, exist_ok=True)
        print(f"Created: {d}/")
    
    # Create __init__.py files
    for d in [root / "agent", root / "tools", root / "tests"]:
        (d / "__init__.py").write_text("")
    
    # Create default config
    config = {
        "agent": {
            "name": project_name,
            "model": "gpt-3.5-turbo",
            "temperature": 0.7,
            "max_tokens": 2048,
        },
        "tools": ["search", "code"],
        "logging": {
            "level": "INFO",
            "file": "logs/agent.log"
        }
    }
    config_path = root / "config" / "default.json"
    config_path.write_text(json.dumps(config, indent=2))
    print(f"Created: {config_path}")
    
    # Create .env template
    env_template = """# AI Agent Environment Variables
OPENAI_API_KEY=your-key-here
LOG_LEVEL=INFO
"""
    (root / ".env.example").write_text(env_template)
    
    # Create .gitignore
    gitignore = """.env
__pycache__/
*.pyc
logs/
ai-agent-env/
.venv/
"""
    (root / ".gitignore").write_text(gitignore)
    
    # Create requirements.txt
    requirements = """openai>=1.12.0
python-dotenv>=1.0.0
requests>=2.31.0
"""
    (root / "requirements.txt").write_text(requirements)
    
    # Create main.py
    main_py = '''"""Main entry point for the AI agent."""

import json
from pathlib import Path

def load_config():
    config_path = Path("config/default.json")
    with open(config_path) as f:
        return json.load(f)

def main():
    config = load_config()
    print(f"Starting {config['agent']['name']}...")
    print(f"Model: {config['agent']['model']}")
    print("Agent ready!")

if __name__ == "__main__":
    main()
'''
    (root / "main.py").write_text(main_py)
    print(f"Created: {root / 'main.py'}")
    
    print(f"\n✅ Project '{project_name}' created successfully!")
    print(f"Next steps:")
    print(f"  cd {project_name}")
    print(f"  python -m venv .venv")
    print(f"  .venv\\Scripts\\activate")
    print(f"  pip install -r requirements.txt")

# Run it
if __name__ == "__main__":
    create_project("my_devops_agent")
```

---

## 7. Exercises

### Exercise 1: Utility Module
```python
# Create a module called `ai_utils.py` with these functions:
# 1. estimate_tokens(text) → int
# 2. truncate_to_tokens(text, max_tokens) → str  (truncate at word boundary)
# 3. hash_prompt(prompt) → str  (short SHA256 hash)
# 4. timestamp() → str  (ISO format)
# 5. format_messages(messages) → str  (pretty-print messages list)
# Then import and use all functions in a separate main.py
```

### Exercise 2: Package Explorer
```python
# Write a script that:
# 1. Takes a package name as input
# 2. Checks if it's installed (try importing it)
# 3. If installed, print its version and location
# 4. If not installed, ask user if they want to install it
# 5. List all installed packages matching a search term
# Hint: use importlib, pkg_resources, or subprocess to run pip
```

### Exercise 3: requirements.txt Generator
```python
# Write a script that:
# 1. Scans all .py files in a directory
# 2. Finds all import statements
# 3. Separates standard library vs third-party imports
# 4. Generates a requirements.txt with the third-party imports
# Hint: sys.stdlib_module_names (Python 3.10+) lists stdlib modules
```

---

## Solutions

See [solutions/day10_solutions.py](../solutions/day10_solutions.py)

---

## Key Takeaways
- `import module` or `from module import item` to use code from other files
- Standard library has tons of useful modules: `json`, `os`, `datetime`, `random`, `collections`
- `if __name__ == "__main__":` prevents code from running on import
- Use `pip install` to get third-party packages
- Always use **virtual environments** to isolate project dependencies
- `requirements.txt` records your project's dependencies

**Tomorrow:** Object-Oriented Programming basics →
