# ============================================
# Day 8 Solutions — File I/O & JSON
# ============================================

import json
from pathlib import Path
from datetime import datetime

# --- Exercise 1: Log File Analyzer ---
print("--- Log File Analyzer ---")

# Create sample log file
sample_logs = """2024-01-15 08:00:01 INFO  Server started on port 8080
2024-01-15 08:02:15 WARNING  High memory usage: 85%
2024-01-15 08:05:30 ERROR  Database connection timeout
2024-01-15 08:06:00 INFO  Retry attempt 1 for database
2024-01-15 08:06:05 INFO  Database reconnected
2024-01-15 08:10:22 WARNING  Disk usage at 90%
2024-01-15 08:15:00 ERROR  Failed to write to /var/log/app.log
2024-01-15 08:15:01 INFO  Switched to backup log path
2024-01-15 08:20:00 INFO  Health check passed
2024-01-15 08:25:33 ERROR  API rate limit exceeded
"""

log_path = Path("sample_server.log")
log_path.write_text(sample_logs)

# Analyze
lines = log_path.read_text().strip().split("\n")
counts = {"INFO": 0, "WARNING": 0, "ERROR": 0}
errors = []

for line in lines:
    for level in counts:
        if level in line:
            counts[level] += 1
            if level == "ERROR":
                errors.append(line)
            break

print(f"Total lines: {len(lines)}")
for level, count in counts.items():
    pct = (count / len(lines)) * 100 if lines else 0
    print(f"  {level}: {count} ({pct:.0f}%)")

print("\nErrors found:")
for err in errors:
    print(f"  ❌ {err}")

# Cleanup
log_path.unlink(missing_ok=True)


# --- Exercise 2: JSON Config Manager ---
print("\n--- JSON Config Manager ---")

default_config = {
    "app_name": "DevOps Bot",
    "version": "1.0",
    "model": "gpt-4o-mini",
    "max_tokens": 500,
    "temperature": 0.7,
    "logging": {"level": "INFO", "file": "app.log"},
    "features": {"streaming": True, "memory": False},
}

config_path = Path("config.json")


def save_config(config: dict, path: Path = config_path):
    path.write_text(json.dumps(config, indent=2))
    print(f"  Config saved to {path}")


def load_config(path: Path = config_path) -> dict:
    if path.exists():
        data = json.loads(path.read_text())
        print(f"  Config loaded from {path}")
        return data
    print("  Config not found, using defaults.")
    return default_config.copy()


def update_config(key: str, value, config: dict) -> dict:
    keys = key.split(".")
    obj = config
    for k in keys[:-1]:
        obj = obj.setdefault(k, {})
    obj[keys[-1]] = value
    print(f"  Updated {key} = {value}")
    return config


# Test
save_config(default_config)
config = load_config()
print(f"  Current model: {config['model']}")

config = update_config("model", "gpt-4o", config)
config = update_config("logging.level", "DEBUG", config)
config = update_config("features.memory", True, config)

save_config(config)
reloaded = load_config()
print(f"  Model after reload: {reloaded['model']}")
print(f"  Logging level: {reloaded['logging']['level']}")

# Cleanup
config_path.unlink(missing_ok=True)


# --- Exercise 3: CSV Report Generator ---
print("\n--- CSV Report Generator ---")

api_calls = [
    {"timestamp": "2024-01-15 08:00", "model": "gpt-4o-mini", "tokens": 150, "status": "success"},
    {"timestamp": "2024-01-15 08:05", "model": "claude-sonnet-4-20250514", "tokens": 500, "status": "success"},
    {"timestamp": "2024-01-15 08:10", "model": "gpt-4o-mini", "tokens": 200, "status": "error"},
    {"timestamp": "2024-01-15 08:15", "model": "gemini-2.0-flash", "tokens": 800, "status": "success"},
    {"timestamp": "2024-01-15 08:20", "model": "gpt-4o-mini", "tokens": 100, "status": "success"},
]

csv_path = Path("api_report.csv")

# Write CSV
header = "timestamp,model,tokens,status\n"
rows = [f"{r['timestamp']},{r['model']},{r['tokens']},{r['status']}" for r in api_calls]
csv_path.write_text(header + "\n".join(rows))
print(f"  CSV written: {csv_path}")

# Read & summarize
csv_lines = csv_path.read_text().strip().split("\n")
total_tokens = sum(r["tokens"] for r in api_calls)
success_count = sum(1 for r in api_calls if r["status"] == "success")
error_count = len(api_calls) - success_count

print(f"  Total API calls: {len(api_calls)}")
print(f"  Success: {success_count}, Errors: {error_count}")
print(f"  Total tokens: {total_tokens}")
print(f"  Average tokens/call: {total_tokens / len(api_calls):.0f}")

# Cleanup
csv_path.unlink(missing_ok=True)
