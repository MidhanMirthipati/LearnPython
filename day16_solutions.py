# ============================================
# Day 16 Solutions — Environment Variables & Secrets
# ============================================

import os
import json
from pathlib import Path


# --- Exercise 1: Config Manager with Env Vars ---
print("--- Config Manager ---")


class Config:
    """Application config from env vars with defaults and validation."""

    DEFAULTS = {
        "APP_NAME": "DevOpsBot",
        "LOG_LEVEL": "INFO",
        "MODEL": "gpt-4o-mini",
        "MAX_TOKENS": "500",
        "TEMPERATURE": "0.7",
        "API_TIMEOUT": "30",
    }

    REQUIRED = ["OPENAI_API_KEY"]  # Or ANTHROPIC_API_KEY or GOOGLE_API_KEY

    def __init__(self, prefix: str = "MYAPP_"):
        self.prefix = prefix
        self._config: dict[str, str] = {}
        self._load()

    def _load(self):
        """Load config from env vars with prefix."""
        for key, default in self.DEFAULTS.items():
            env_key = f"{self.prefix}{key}"
            self._config[key] = os.environ.get(env_key, default)

        # Check required vars
        missing = []
        for key in self.REQUIRED:
            env_key = f"{self.prefix}{key}"
            val = os.environ.get(env_key, "")
            if val:
                self._config[key] = val
            else:
                missing.append(env_key)

        if missing:
            print(f"  ⚠️ Missing env vars: {missing} (using placeholder)")
            for key in self.REQUIRED:
                self._config.setdefault(key, "NOT_SET")

    def get(self, key: str, default: str = "") -> str:
        return self._config.get(key, default)

    def get_int(self, key: str, default: int = 0) -> int:
        try:
            return int(self._config.get(key, str(default)))
        except ValueError:
            return default

    def get_float(self, key: str, default: float = 0.0) -> float:
        try:
            return float(self._config.get(key, str(default)))
        except ValueError:
            return default

    def is_set(self, key: str) -> bool:
        val = self._config.get(key, "NOT_SET")
        return val != "NOT_SET" and val != ""

    def display(self, mask_secrets: bool = True):
        """Print config, masking sensitive values."""
        secret_keys = {"API_KEY", "SECRET", "PASSWORD", "TOKEN"}
        for key, value in sorted(self._config.items()):
            is_secret = any(s in key.upper() for s in secret_keys)
            display_val = "****" + value[-4:] if is_secret and mask_secrets and len(value) > 4 else value
            print(f"  {key}: {display_val}")


# Test
config = Config()
config.display()
print(f"\n  Model: {config.get('MODEL')}")
print(f"  Max tokens: {config.get_int('MAX_TOKENS')}")
print(f"  Temperature: {config.get_float('TEMPERATURE')}")
print(f"  API Key set: {config.is_set('OPENAI_API_KEY')}")


# --- Exercise 2: .env File Parser ---
print("\n--- .env File Parser ---")


def parse_env_file(filepath: str) -> dict[str, str]:
    """Parse a .env file into a dictionary."""
    env_vars = {}
    path = Path(filepath)

    if not path.exists():
        print(f"  File not found: {filepath}")
        return env_vars

    for line_num, line in enumerate(path.read_text().splitlines(), 1):
        # Skip empty lines and comments
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # Parse KEY=VALUE
        if "=" not in stripped:
            print(f"  Warning line {line_num}: No '=' found, skipping")
            continue

        key, _, value = stripped.partition("=")
        key = key.strip()
        value = value.strip()

        # Remove surrounding quotes
        if (value.startswith('"') and value.endswith('"')) or \
           (value.startswith("'") and value.endswith("'")):
            value = value[1:-1]

        env_vars[key] = value

    return env_vars


def create_env_template(config_keys: list[str], output_path: str = ".env.example"):
    """Create a .env.example template file."""
    lines = ["# Application Configuration", "# Copy to .env and fill in values", ""]
    for key in config_keys:
        lines.append(f"{key}=")
    Path(output_path).write_text("\n".join(lines))
    print(f"  Template created: {output_path}")


# Create test .env file
test_env = """# Test configuration
APP_NAME=MyBot
MODEL="gpt-4o-mini"
OPENAI_API_KEY='sk-test123456789'
ANTHROPIC_API_KEY='sk-ant-test123456789'
GOOGLE_API_KEY='test-google-key-123'
MAX_TOKENS=1000
# This is a comment
TEMPERATURE=0.8
"""

test_env_path = Path("test.env")
test_env_path.write_text(test_env)

parsed = parse_env_file("test.env")
print("Parsed .env:")
for key, value in parsed.items():
    masked = "****" if "KEY" in key else value
    print(f"  {key} = {masked}")

# Cleanup
test_env_path.unlink(missing_ok=True)

# Create template
create_env_template(["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_API_KEY", "LLM_PROVIDER", "MODEL", "MAX_TOKENS", "LOG_LEVEL"])
Path(".env.example").unlink(missing_ok=True)


# --- Exercise 3: Secret Rotation Simulator ---
print("\n--- Secret Rotation Simulator ---")

import hashlib
from datetime import datetime, timedelta
import random
import string


def generate_api_key(prefix: str = "sk-") -> str:
    """Generate a random API key."""
    chars = string.ascii_letters + string.digits
    random_part = "".join(random.choices(chars, k=40))
    return f"{prefix}{random_part}"


class SecretManager:
    """Manages API keys with rotation tracking."""

    def __init__(self):
        self.secrets: dict[str, dict] = {}

    def create(self, name: str) -> str:
        key = generate_api_key()
        self.secrets[name] = {
            "key": key,
            "created_at": datetime.now().isoformat(),
            "rotated_count": 0,
            "hash": hashlib.sha256(key.encode()).hexdigest()[:16],
        }
        print(f"  Created: {name} (hash: {self.secrets[name]['hash']})")
        return key

    def rotate(self, name: str) -> str | None:
        if name not in self.secrets:
            print(f"  Secret '{name}' not found")
            return None
        old_hash = self.secrets[name]["hash"]
        new_key = generate_api_key()
        self.secrets[name]["key"] = new_key
        self.secrets[name]["rotated_count"] += 1
        self.secrets[name]["last_rotated"] = datetime.now().isoformat()
        self.secrets[name]["hash"] = hashlib.sha256(new_key.encode()).hexdigest()[:16]
        print(f"  Rotated: {name} (old: {old_hash} → new: {self.secrets[name]['hash']})")
        return new_key

    def verify(self, name: str, key: str) -> bool:
        if name not in self.secrets:
            return False
        return self.secrets[name]["key"] == key

    def list_secrets(self):
        for name, info in self.secrets.items():
            print(f"  {name}: hash={info['hash']}, rotations={info['rotated_count']}")


# Test
mgr = SecretManager()
key1 = mgr.create("openai")
key2 = mgr.create("github")

print(f"\n  Verify openai: {mgr.verify('openai', key1)}")
print(f"  Verify wrong:  {mgr.verify('openai', 'wrong-key')}")

mgr.rotate("openai")
print(f"  Verify old key: {mgr.verify('openai', key1)}")

print("\nAll secrets:")
mgr.list_secrets()
