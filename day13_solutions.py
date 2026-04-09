# ============================================
# Day 13 Solutions — Comprehensions & Generators
# ============================================

import time


# --- Exercise 1: Data Transformation Pipeline ---
print("--- Data Transformation Pipeline ---")

# Sample raw data from "API"
raw_responses = [
    {"model": "gpt-4o", "tokens": 500, "latency_ms": 1200, "status": "success", "content": "Docker is a platform..."},
    {"model": "claude-sonnet", "tokens": 150, "latency_ms": 300, "status": "success", "content": "Hello!"},
    {"model": "gpt-4o", "tokens": 0, "latency_ms": 5000, "status": "error", "content": ""},
    {"model": "gemini-flash", "tokens": 200, "latency_ms": 400, "status": "success", "content": "Kubernetes orchestrates..."},
    {"model": "gpt-4o", "tokens": 800, "latency_ms": 2000, "status": "success", "content": "CI/CD is the practice of..."},
    {"model": "claude-sonnet", "tokens": 50, "latency_ms": 8000, "status": "error", "content": ""},
    {"model": "gemini-flash", "tokens": 350, "latency_ms": 900, "status": "success", "content": "Terraform enables..."},
]

# 1. List comprehension: successful responses only
successful = [r for r in raw_responses if r["status"] == "success"]
print(f"Successful responses: {len(successful)}/{len(raw_responses)}")

# 2. Dict comprehension: model → average latency
from collections import defaultdict
model_latencies = defaultdict(list)
for r in raw_responses:
    model_latencies[r["model"]].append(r["latency_ms"])

avg_latency = {model: sum(lats) / len(lats) for model, lats in model_latencies.items()}
print(f"Avg latency: {avg_latency}")

# 3. Nested comprehension: extract first word of each successful content
first_words = [r["content"].split()[0] for r in successful if r["content"]]
print(f"First words: {first_words}")

# 4. Set comprehension: unique models
unique_models = {r["model"] for r in raw_responses}
print(f"Unique models: {unique_models}")

# 5. Dict comprehension: cost per response
RATES = {"gpt-4o": 0.005, "claude-sonnet": 0.003, "gemini-flash": 0.0001}
costs = {i: (r["tokens"] / 1000) * RATES.get(r["model"], 0) for i, r in enumerate(raw_responses)}
print(f"Costs: {costs}")
print(f"Total cost: ${sum(costs.values()):.4f}")


# --- Exercise 2: Log Stream Generator ---
print("\n--- Log Stream Generator ---")


def log_generator(log_lines: list[str]):
    """Yield parsed log entries one at a time."""
    for line in log_lines:
        parts = line.split(maxsplit=3)
        if len(parts) >= 4:
            yield {
                "date": parts[0],
                "time": parts[1],
                "level": parts[2],
                "message": parts[3],
            }


def filter_by_level(logs, level: str):
    """Generator that filters logs by level."""
    for log in logs:
        if log["level"] == level:
            yield log


def batch_logs(logs, batch_size: int = 3):
    """Yield logs in batches."""
    batch = []
    for log in logs:
        batch.append(log)
        if len(batch) == batch_size:
            yield batch
            batch = []
    if batch:
        yield batch


sample_log_lines = [
    "2024-01-15 08:00:01 INFO Server started",
    "2024-01-15 08:02:15 WARNING High memory: 85%",
    "2024-01-15 08:05:30 ERROR DB connection timeout",
    "2024-01-15 08:06:00 INFO Retry attempt 1",
    "2024-01-15 08:06:05 INFO DB reconnected",
    "2024-01-15 08:10:22 WARNING Disk at 90%",
    "2024-01-15 08:15:00 ERROR Write failed",
    "2024-01-15 08:15:01 INFO Backup log active",
    "2024-01-15 08:20:00 INFO Health check OK",
]

# Chain generators
all_logs = log_generator(sample_log_lines)
error_logs = filter_by_level(log_generator(sample_log_lines), "ERROR")

print("All logs (first 3):")
for log in list(log_generator(sample_log_lines))[:3]:
    print(f"  {log['level']}: {log['message']}")

print("\nErrors only:")
for log in filter_by_level(log_generator(sample_log_lines), "ERROR"):
    print(f"  ❌ {log['message']}")

print("\nBatched (size 3):")
for i, batch in enumerate(batch_logs(log_generator(sample_log_lines), 3)):
    print(f"  Batch {i+1}: {[l['level'] for l in batch]}")


# --- Exercise 3: Lazy Token Counter ---
print("\n--- Lazy Token Counter ---")


def token_counter(messages: list[str]):
    """Generator that yields cumulative token counts."""
    total = 0
    for msg in messages:
        tokens = max(1, len(msg) // 4)
        total += tokens
        yield {
            "message": msg[:40],
            "tokens": tokens,
            "cumulative": total,
        }


def budget_monitor(token_stream, budget: int):
    """Generator that monitors budget and warns when close."""
    for item in token_stream:
        pct = (item["cumulative"] / budget) * 100
        item["budget_pct"] = pct
        item["status"] = (
            "OVER" if pct > 100
            else "CRITICAL" if pct > 90
            else "WARNING" if pct > 75
            else "OK"
        )
        yield item
        if pct > 100:
            return  # Stop processing


messages = [
    "Hello, how are you?",
    "Explain Docker networking in detail with examples",
    "What is Kubernetes and how does it compare to Docker Swarm?",
    "Write a comprehensive Terraform module for AWS ECS with auto-scaling",
    "Summarize the differences between microservices and monolithic architectures",
    "One more small question",
]

BUDGET = 50

print(f"Budget: {BUDGET} tokens\n")
stream = token_counter(messages)
monitored = budget_monitor(stream, BUDGET)

for item in monitored:
    status_emoji = {"OK": "✅", "WARNING": "⚠️", "CRITICAL": "🚨", "OVER": "❌"}
    emoji = status_emoji[item["status"]]
    print(f"  {emoji} {item['status']:<8} | +{item['tokens']:>3} tokens | "
          f"Total: {item['cumulative']:>4} ({item['budget_pct']:.0f}%) | "
          f"\"{item['message']}\"")
