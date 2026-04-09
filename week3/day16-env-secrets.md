# Day 16: Environment Variables & Secrets Management

## Learning Goals
- Store API keys securely (never hard-code!)
- Use .env files with python-dotenv
- Understand configuration hierarchy
- Build a secure configuration loader

---

## 1. Why This Matters

```python
# ❌ NEVER do this — API key in source code
api_key = "sk-abc123..."  # Gets committed to Git = leaked to the world

# ✅ Always load from environment
import os
openai_key = os.environ.get("OPENAI_API_KEY")
anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
google_key = os.environ.get("GOOGLE_API_KEY")
```

If your API key leaks:
- Anyone can make API calls on your account
- You get billed for their usage
- Automated bots scan GitHub for leaked keys within minutes

---

## 2. Environment Variables

```python
import os

# Read environment variables for your LLM providers
openai_key = os.environ.get("OPENAI_API_KEY")
anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
google_key = os.environ.get("GOOGLE_API_KEY")

# With a default value
model = os.environ.get("DEFAULT_MODEL", "gpt-4o-mini")
llm_provider = os.environ.get("LLM_PROVIDER", "openai")  # openai | anthropic | gemini

# Check that at least one provider key is configured
if not any([openai_key, anthropic_key, google_key]):
    raise EnvironmentError(
        "At least one LLM API key is required. Set one of:\n"
        "  OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY\n"
        "  Example: $env:OPENAI_API_KEY='sk-your-key'"
    )

# Set environment variable (current process only)
os.environ["MY_SETTING"] = "value"
```

### Setting Environment Variables

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY = "sk-your-key-here"
$env:ANTHROPIC_API_KEY = "sk-ant-your-key-here"
$env:GOOGLE_API_KEY = "your-google-key-here"
$env:LLM_PROVIDER = "openai"  # or "anthropic" or "gemini"
```

**Windows (cmd):**
```cmd
set OPENAI_API_KEY=sk-your-key-here
set ANTHROPIC_API_KEY=sk-ant-your-key-here
set GOOGLE_API_KEY=your-google-key-here
```

**Linux/Mac:**
```bash
export OPENAI_API_KEY="sk-your-key-here"
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
export GOOGLE_API_KEY="your-google-key-here"
```

---

## 3. Using .env Files (python-dotenv)

```bash
pip install python-dotenv
```

### Create a `.env` file
```ini
# .env — NEVER commit this file to Git!

# LLM Provider Keys (add the ones you have)
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
GOOGLE_API_KEY=your-google-key-here

# LLM Settings
LLM_PROVIDER=openai
DEFAULT_MODEL=gpt-4o-mini
TEMPERATURE=0.7
MAX_TOKENS=2048
LOG_LEVEL=INFO
DATABASE_URL=postgresql://user:pass@localhost/db
```

### Create a `.env.example` file (DO commit this)
```ini
# .env.example — Template for required environment variables
# Get at least one API key from:
#   OpenAI:    https://platform.openai.com/api-keys
#   Anthropic: https://console.anthropic.com/settings/keys
#   Gemini:    https://aistudio.google.com/app/apikey

OPENAI_API_KEY=your-openai-key-here
ANTHROPIC_API_KEY=your-anthropic-key-here
GOOGLE_API_KEY=your-google-key-here
LLM_PROVIDER=openai
DEFAULT_MODEL=gpt-4o-mini
TEMPERATURE=0.7
MAX_TOKENS=2048
LOG_LEVEL=INFO
```

### Load and use
```python
from dotenv import load_dotenv
import os

# Load .env file into environment
load_dotenv()

# Now read as normal
api_key = os.environ.get("OPENAI_API_KEY")
provider = os.environ.get("LLM_PROVIDER", "openai")
model = os.environ.get("DEFAULT_MODEL", "gpt-4o-mini")
temperature = float(os.environ.get("TEMPERATURE", "0.7"))
max_tokens = int(os.environ.get("MAX_TOKENS", "2048"))

print(f"Model: {model}, Temp: {temperature}, Max Tokens: {max_tokens}")
```

### .gitignore (critical!)
```gitignore
# Always ignore .env files
.env
.env.local
.env.production

# Keep the example
!.env.example
```

---

## 4. Configuration Class

```python
from dotenv import load_dotenv
import os
from dataclasses import dataclass

load_dotenv()

@dataclass
class Config:
    """Type-safe configuration loaded from environment."""
    llm_provider: str
    openai_api_key: str | None
    anthropic_api_key: str | None
    google_api_key: str | None
    model: str
    temperature: float
    max_tokens: int
    log_level: str
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        openai_key = os.environ.get("OPENAI_API_KEY")
        anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
        google_key = os.environ.get("GOOGLE_API_KEY")
        
        if not any([openai_key, anthropic_key, google_key]):
            raise EnvironmentError(
                "At least one LLM API key is required. "
                "Set OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY."
            )
        
        provider = os.environ.get("LLM_PROVIDER", "openai")
        default_models = {
            "openai": "gpt-4o-mini",
            "anthropic": "claude-sonnet-4-20250514",
            "gemini": "gemini-2.0-flash",
        }
        
        return cls(
            llm_provider=provider,
            openai_api_key=openai_key,
            anthropic_api_key=anthropic_key,
            google_api_key=google_key,
            model=os.environ.get("DEFAULT_MODEL", default_models.get(provider, "gpt-4o-mini")),
            temperature=float(os.environ.get("TEMPERATURE", "0.7")),
            max_tokens=int(os.environ.get("MAX_TOKENS", "2048")),
            log_level=os.environ.get("LOG_LEVEL", "INFO"),
        )
    
    def __str__(self):
        """Print config WITHOUT exposing secrets."""
        def mask(key):
            return ('***' + key[-4:]) if key else 'not set'
        return (
            f"Config(provider={self.llm_provider}, model={self.model}, "
            f"temperature={self.temperature}, max_tokens={self.max_tokens}, "
            f"openai_key={mask(self.openai_api_key)}, "
            f"anthropic_key={mask(self.anthropic_api_key)}, "
            f"google_key={mask(self.google_api_key)})"
        )

# Usage
config = Config.from_env()
print(config)  # api_key is masked!
```

---

## 5. Configuration Hierarchy

Priority order (highest to lowest):
1. Command-line arguments
2. Environment variables
3. `.env` file
4. Config file (JSON/YAML)
5. Default values

```python
import json
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def load_config(config_path: str = "config.json") -> dict:
    """Load config with proper priority."""
    
    # Start with defaults
    config = {
        "llm_provider": "openai",
        "model": "gpt-4o-mini",
        "temperature": 0.7,
        "max_tokens": 2048,
    }
    
    # Override with config file
    if Path(config_path).exists():
        with open(config_path) as f:
            file_config = json.load(f)
            config.update(file_config)
    
    # Override with environment variables
    env_mapping = {
        "DEFAULT_MODEL": "model",
        "TEMPERATURE": "temperature",
        "MAX_TOKENS": "max_tokens",
    }
    
    for env_key, config_key in env_mapping.items():
        env_value = os.environ.get(env_key)
        if env_value:
            # Type conversion
            if config_key == "temperature":
                config[config_key] = float(env_value)
            elif config_key == "max_tokens":
                config[config_key] = int(env_value)
            else:
                config[config_key] = env_value
    
    return config
```

---

## 6. Exercises

### Exercise 1: Secure Config Loader
```python
# Build a SecureConfig class that:
# 1. Loads from .env file
# 2. Validates all required keys are present
# 3. Masks sensitive values when printed (keys, passwords, tokens)
# 4. Has a to_dict() method that excludes secrets
# 5. Has a validate() method that checks value ranges
#    (temperature 0-2, max_tokens > 0, model in allowed list)
```

### Exercise 2: Multi-Environment Setup
```python
# Build a system that loads different configs for different environments:
# - .env.development (local dev settings)
# - .env.staging (staging settings)
# - .env.production (prod settings)
# Load based on APP_ENV environment variable
# Default to "development"
```

### Exercise 3: Config File Generator
```python
# Build a script that:
# 1. Asks the user for their API key, preferred model, etc.
# 3. Validates the API key format (OpenAI starts with "sk-", Anthropic with "sk-ant-", etc.)
# 4. Generates a .env file with keys for all configured providers
# 4. Generates a .env.example file (same keys, placeholder values)
# 5. Checks if .gitignore exists and adds .env if missing
```

---

## Solutions

See [solutions/day16_solutions.py](../solutions/day16_solutions.py)

---

## Key Takeaways
- **NEVER** hard-code API keys, passwords, or secrets in source code
- Use `.env` files + `python-dotenv` for local development
- Always add `.env` to `.gitignore`
- Commit a `.env.example` as a template
- Mask secrets when logging or printing config
- Use a Config class for type-safe, validated configuration

**Tomorrow:** Calling LLM APIs (OpenAI, Anthropic, Gemini) →
