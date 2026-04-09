# ============================================
# Capstone Project — DevOps Assistant Agent
# Configuration Module
# ============================================

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# --- Application Settings ---
APP_NAME = "DevOps Assistant Agent"
APP_VERSION = "1.0.0"

# --- LLM Settings ---
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "openai")  # openai | anthropic | gemini
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")

_DEFAULT_MODELS = {"openai": "gpt-4o-mini", "anthropic": "claude-sonnet-4-20250514", "gemini": "gemini-2.0-flash"}
MODEL = os.environ.get("MODEL", _DEFAULT_MODELS.get(LLM_PROVIDER, "gpt-4o-mini"))
MAX_TOKENS = int(os.environ.get("MAX_TOKENS", "1000"))
TEMPERATURE = float(os.environ.get("TEMPERATURE", "0.7"))

# --- Agent Settings ---
MAX_AGENT_STEPS = int(os.environ.get("MAX_AGENT_STEPS", "5"))
MEMORY_WINDOW_SIZE = int(os.environ.get("MEMORY_WINDOW_SIZE", "20"))
TOKEN_BUDGET = int(os.environ.get("TOKEN_BUDGET", "4000"))

# --- Guardrails ---
MAX_INPUT_LENGTH = 2000
MAX_OUTPUT_LENGTH = 5000
BLOCKED_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|above)\s+instructions",
    r"you\s+are\s+now",
    r"pretend\s+to\s+be",
    r"reveal\s+your\s+(system|original)\s+prompt",
]

# --- Logging ---
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

# --- System Prompt ---
SYSTEM_PROMPT = """You are a DevOps Assistant Agent. You help users with:
- Docker container management
- Kubernetes cluster operations
- CI/CD pipeline configuration
- Infrastructure monitoring
- Cloud resource management

You have access to tools. Use them when needed to provide accurate, actionable answers.
Always explain what you're doing and why. Be concise but thorough."""

# --- Validation ---
def validate_config() -> list[str]:
    """Check configuration and return any warnings."""
    warnings = []
    if not any([OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY]):
        warnings.append("No LLM API key set — will use simulated responses")
    if MAX_TOKENS > 4000:
        warnings.append(f"MAX_TOKENS={MAX_TOKENS} is high — may increase costs")
    if TEMPERATURE > 1.0:
        warnings.append(f"TEMPERATURE={TEMPERATURE} is above 1.0 — outputs may be erratic")
    return warnings


def display_config():
    """Print current configuration (masking secrets)."""
    key_display = f"****{OPENAI_API_KEY[-4:]}" if OPENAI_API_KEY else "(not set)"
    anthropic_display = f"****{ANTHROPIC_API_KEY[-4:]}" if ANTHROPIC_API_KEY else "(not set)"
    google_display = f"****{GOOGLE_API_KEY[-4:]}" if GOOGLE_API_KEY else "(not set)"
    print(f"""
  {APP_NAME} v{APP_VERSION}
  ─────────────────────────────
  Provider:    {LLM_PROVIDER}
  Model:       {MODEL}
  Max Tokens:  {MAX_TOKENS}
  Temperature: {TEMPERATURE}
  OpenAI Key:  {key_display}
  Anthropic:   {anthropic_display}
  Google Key:  {google_display}
  Agent Steps: {MAX_AGENT_STEPS}
  Memory:      {MEMORY_WINDOW_SIZE} messages
  Log Level:   {LOG_LEVEL}
""")
    warnings = validate_config()
    if warnings:
        for w in warnings:
            print(f"  ⚠️  {w}")
