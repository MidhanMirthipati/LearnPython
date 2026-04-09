# ============================================
# Day 19 Solutions — Working with Data (pandas)
# ============================================

# NOTE: Requires pandas. Install with: pip install pandas

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    print("[INFO] pandas not installed. Run: pip install pandas")

import json
from datetime import datetime, timedelta
import random


# --- Exercise 1: API Usage Analytics Dashboard ---
print("--- API Usage Analytics ---")

if HAS_PANDAS:
    # Generate sample data
    random.seed(42)
    models = ["gpt-4o-mini", "claude-sonnet", "gemini-flash"]
    statuses = ["success", "success", "success", "success", "error"]  # 80% success rate

    data = []
    base_time = datetime(2024, 1, 15, 8, 0, 0)
    for i in range(100):
        model = random.choice(models)
        tokens = random.randint(50, 2000)
        cost_rate = {"gpt-4o-mini": 0.00015, "claude-sonnet": 0.003, "gemini-flash": 0.0001}
        data.append({
            "timestamp": (base_time + timedelta(minutes=i * 5)).isoformat(),
            "model": model,
            "tokens": tokens,
            "cost": round(tokens / 1000 * cost_rate[model], 4),
            "latency_ms": random.randint(100, 3000),
            "status": random.choice(statuses),
        })

    df = pd.DataFrame(data)

    # 1. Basic stats
    print(f"\nTotal API calls: {len(df)}")
    print(f"Date range: {df['timestamp'].min()} → {df['timestamp'].max()}")
    print(f"\nStatus breakdown:")
    print(df["status"].value_counts().to_string())

    # 2. Per-model analysis
    print(f"\nPer-model summary:")
    model_stats = df.groupby("model").agg(
        calls=("model", "count"),
        avg_tokens=("tokens", "mean"),
        total_cost=("cost", "sum"),
        avg_latency=("latency_ms", "mean"),
        error_rate=("status", lambda x: (x == "error").mean()),
    ).round(3)
    print(model_stats.to_string())

    # 3. Top 5 most expensive calls
    print(f"\nTop 5 most expensive calls:")
    top5 = df.nlargest(5, "cost")[["model", "tokens", "cost", "latency_ms"]]
    print(top5.to_string(index=False))

    # 4. Hourly aggregation
    df["hour"] = pd.to_datetime(df["timestamp"]).dt.hour
    hourly = df.groupby("hour").agg(
        calls=("hour", "count"),
        total_tokens=("tokens", "sum"),
        total_cost=("cost", "sum"),
    )
    print(f"\nHourly usage:")
    print(hourly.to_string())

else:
    print("  Skipping — pandas not available")


# --- Exercise 2: Log DataFrame Analyzer ---
print("\n--- Log DataFrame Analyzer ---")

if HAS_PANDAS:
    log_data = [
        {"timestamp": "2024-01-15 08:00:01", "level": "INFO", "service": "api", "message": "Server started"},
        {"timestamp": "2024-01-15 08:02:15", "level": "WARNING", "service": "api", "message": "High memory 85%"},
        {"timestamp": "2024-01-15 08:05:30", "level": "ERROR", "service": "db", "message": "Connection timeout"},
        {"timestamp": "2024-01-15 08:06:00", "level": "INFO", "service": "db", "message": "Retry attempt 1"},
        {"timestamp": "2024-01-15 08:06:05", "level": "INFO", "service": "db", "message": "Reconnected"},
        {"timestamp": "2024-01-15 08:10:22", "level": "WARNING", "service": "storage", "message": "Disk at 90%"},
        {"timestamp": "2024-01-15 08:15:00", "level": "ERROR", "service": "storage", "message": "Write failed"},
        {"timestamp": "2024-01-15 08:15:01", "level": "INFO", "service": "storage", "message": "Backup log active"},
        {"timestamp": "2024-01-15 08:20:00", "level": "INFO", "service": "api", "message": "Health check OK"},
        {"timestamp": "2024-01-15 08:25:33", "level": "ERROR", "service": "api", "message": "Rate limit hit"},
    ]

    logs_df = pd.DataFrame(log_data)
    logs_df["timestamp"] = pd.to_datetime(logs_df["timestamp"])

    # Level counts
    print("Log level distribution:")
    print(logs_df["level"].value_counts().to_string())

    # Errors by service
    errors = logs_df[logs_df["level"] == "ERROR"]
    print(f"\nErrors by service:")
    print(errors.groupby("service")["message"].count().to_string())

    # Service health summary
    print(f"\nService health:")
    for service in logs_df["service"].unique():
        svc = logs_df[logs_df["service"] == service]
        error_count = len(svc[svc["level"] == "ERROR"])
        total = len(svc)
        health = "UNHEALTHY" if error_count > 0 else "HEALTHY"
        print(f"  {service}: {health} ({error_count}/{total} errors)")

else:
    print("  Skipping — pandas not available")


# --- Exercise 3: Data Export Pipeline ---
print("\n--- Data Export Pipeline ---")

if HAS_PANDAS:
    from pathlib import Path

    # Create summary report
    report = {
        "generated_at": datetime.now().isoformat(),
        "total_calls": len(df),
        "total_cost": round(df["cost"].sum(), 4),
        "avg_latency_ms": round(df["latency_ms"].mean(), 1),
        "error_rate": round((df["status"] == "error").mean(), 3),
        "model_breakdown": df.groupby("model")["cost"].sum().round(4).to_dict(),
    }

    # Export to JSON
    report_path = Path("api_report.json")
    report_path.write_text(json.dumps(report, indent=2))
    print(f"  JSON report saved: {report_path}")
    print(f"  Contents: {json.dumps(report, indent=2)[:200]}...")

    # Export to CSV
    csv_path = Path("api_calls.csv")
    df.to_csv(csv_path, index=False)
    print(f"  CSV exported: {csv_path} ({len(df)} rows)")

    # Cleanup
    report_path.unlink(missing_ok=True)
    csv_path.unlink(missing_ok=True)

else:
    print("  Skipping — pandas not available")
