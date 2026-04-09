# ============================================
# Day 10 Solutions — Modules, Packages & pip
# ============================================

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
import hashlib
import platform


# --- Exercise 1: System Info Collector ---
print("--- System Info Collector ---")


def collect_system_info() -> dict:
    info = {
        "python_version": sys.version,
        "platform": platform.platform(),
        "architecture": platform.architecture()[0],
        "hostname": platform.node(),
        "processor": platform.processor(),
        "cwd": os.getcwd(),
        "env_vars": {
            "PATH_entries": len(os.environ.get("PATH", "").split(os.pathsep)),
            "HOME": os.environ.get("HOME") or os.environ.get("USERPROFILE", "N/A"),
            "SHELL": os.environ.get("SHELL") or os.environ.get("COMSPEC", "N/A"),
        },
        "timestamp": datetime.now().isoformat(),
    }
    return info


info = collect_system_info()
print(json.dumps(info, indent=2))


# --- Exercise 2: Date Utility Module ---
print("\n--- Date Utility Module ---")


def days_until(target_date: str) -> int:
    """Days from today to a target date (YYYY-MM-DD)."""
    target = datetime.strptime(target_date, "%Y-%m-%d")
    delta = target - datetime.now()
    return delta.days


def human_time_ago(timestamp: str) -> str:
    """Convert ISO timestamp to human-readable 'X ago' format."""
    dt = datetime.fromisoformat(timestamp)
    diff = datetime.now() - dt
    seconds = int(diff.total_seconds())

    if seconds < 60:
        return f"{seconds} seconds ago"
    elif seconds < 3600:
        return f"{seconds // 60} minutes ago"
    elif seconds < 86400:
        return f"{seconds // 3600} hours ago"
    else:
        return f"{seconds // 86400} days ago"


def generate_date_range(start: str, days: int) -> list[str]:
    """Generate a list of date strings starting from start."""
    start_dt = datetime.strptime(start, "%Y-%m-%d")
    return [(start_dt + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)]


# Test
future = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
print(f"Days until {future}: {days_until(future)}")

past = (datetime.now() - timedelta(hours=3)).isoformat()
print(f"Time since {past[:19]}: {human_time_ago(past)}")

dates = generate_date_range("2024-01-01", 5)
print(f"Date range: {dates}")


# --- Exercise 3: Hashing & Secrets Module ---
print("\n--- Hashing Utility ---")


def hash_text(text: str, algorithm: str = "sha256") -> str:
    """Hash text with the specified algorithm."""
    h = hashlib.new(algorithm)
    h.update(text.encode())
    return h.hexdigest()


def hash_file(filepath: str, algorithm: str = "sha256") -> str | None:
    """Hash a file's contents."""
    path = Path(filepath)
    if not path.exists():
        return None
    h = hashlib.new(algorithm)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()


def compare_hashes(text1: str, text2: str) -> bool:
    return hash_text(text1) == hash_text(text2)


# Test
test_text = "Hello, DevOps World!"
print(f"SHA-256: {hash_text(test_text)}")
print(f"MD5:     {hash_text(test_text, 'md5')}")
print(f"SHA-1:   {hash_text(test_text, 'sha1')}")

# Hash a file
test_path = Path("hash_test.txt")
test_path.write_text("Test file for hashing")
file_hash = hash_file("hash_test.txt")
print(f"File hash: {file_hash}")
test_path.unlink(missing_ok=True)

# Compare
print(f"Same text: {compare_hashes('hello', 'hello')}")
print(f"Diff text: {compare_hashes('hello', 'world')}")
