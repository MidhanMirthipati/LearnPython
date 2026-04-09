# Day 19: Working with Data — Pandas Basics

## Learning Goals
- Load and explore data with Pandas
- Filter, sort, and transform DataFrames
- Aggregate and group data
- Prepare data for AI pipelines

---

## 1. Why Pandas for AI?

AI agents often need to:
- Analyze logs and metrics
- Process CSV/JSON data  
- Prepare training data
- Generate reports from structured data

```bash
pip install pandas
```

---

## 2. Creating DataFrames

```python
import pandas as pd

# From a dictionary
data = {
    "model": ["GPT-4", "Claude-3", "Gemini", "GPT-3.5", "LLaMA-3"],
    "score": [92.5, 91.8, 90.3, 85.2, 88.7],
    "cost_per_1k": [0.03, 0.015, 0.001, 0.002, 0.0],
    "provider": ["OpenAI", "Anthropic", "Google", "OpenAI", "Meta"],
    "release_year": [2023, 2024, 2024, 2022, 2024]
}

df = pd.DataFrame(data)
print(df)

# From a CSV file
# df = pd.read_csv("models.csv")

# From JSON
# df = pd.read_json("models.json")
```

---

## 3. Exploring Data

```python
# Basic info
print(df.shape)          # (5, 5) — rows, columns
print(df.dtypes)         # Data types of each column
print(df.info())         # Summary
print(df.describe())     # Statistical summary (count, mean, std, etc.)

# View data
print(df.head(3))        # First 3 rows
print(df.tail(2))        # Last 2 rows
print(df.columns.tolist())  # Column names

# Single column
print(df["model"])       # Series (single column)
print(df["score"].mean()) # 89.7
print(df["score"].max())  # 92.5
```

---

## 4. Filtering Data

```python
# Boolean filtering
high_scorers = df[df["score"] > 90]
print(high_scorers)

# Multiple conditions
openai_good = df[(df["provider"] == "OpenAI") & (df["score"] > 85)]
print(openai_good)

# Using isin
target_providers = ["OpenAI", "Anthropic"]
filtered = df[df["provider"].isin(target_providers)]
print(filtered)

# String methods
contains_gpt = df[df["model"].str.contains("GPT")]
print(contains_gpt)
```

---

## 5. Sorting and Ranking

```python
# Sort by score (descending)
sorted_df = df.sort_values("score", ascending=False)
print(sorted_df)

# Sort by multiple columns
sorted_df = df.sort_values(["provider", "score"], ascending=[True, False])
print(sorted_df)

# Add a rank column
df["rank"] = df["score"].rank(ascending=False).astype(int)
print(df)
```

---

## 6. Adding and Transforming Columns

```python
# New column from calculation
df["cost_per_point"] = df["cost_per_1k"] / df["score"]

# Conditional column
df["tier"] = df["score"].apply(lambda s: "Top" if s > 90 else "Standard")

# Apply a function
def classify_cost(cost):
    if cost == 0:
        return "Free"
    elif cost < 0.005:
        return "Budget"
    elif cost < 0.02:
        return "Mid"
    else:
        return "Premium"

df["cost_tier"] = df["cost_per_1k"].apply(classify_cost)
print(df[["model", "cost_per_1k", "cost_tier"]])
```

---

## 7. Grouping and Aggregation

```python
# Group by provider
provider_stats = df.groupby("provider").agg({
    "score": ["mean", "max", "count"],
    "cost_per_1k": "mean"
}).round(3)
print(provider_stats)

# Simple group operations
print(df.groupby("provider")["score"].mean())
print(df.groupby("cost_tier")["model"].count())

# Value counts
print(df["provider"].value_counts())
print(df["tier"].value_counts())
```

---

## 8. Practical: API Usage Analyzer

```python
import pandas as pd
import json

# Simulate API usage log
usage_data = [
    {"timestamp": "2024-01-15 10:00", "model": "gpt-4", "tokens": 1500, "cost": 0.045, "status": "success"},
    {"timestamp": "2024-01-15 10:05", "model": "gpt-3.5", "tokens": 800, "cost": 0.0016, "status": "success"},
    {"timestamp": "2024-01-15 10:10", "model": "gpt-4", "tokens": 2000, "cost": 0.06, "status": "success"},
    {"timestamp": "2024-01-15 10:15", "model": "gpt-4", "tokens": 500, "cost": 0.015, "status": "error"},
    {"timestamp": "2024-01-15 10:20", "model": "gpt-3.5", "tokens": 600, "cost": 0.0012, "status": "success"},
    {"timestamp": "2024-01-15 10:25", "model": "claude", "tokens": 1200, "cost": 0.018, "status": "success"},
    {"timestamp": "2024-01-15 10:30", "model": "gpt-4", "tokens": 1800, "cost": 0.054, "status": "success"},
    {"timestamp": "2024-01-15 10:35", "model": "claude", "tokens": 900, "cost": 0.0135, "status": "error"},
    {"timestamp": "2024-01-15 10:40", "model": "gpt-3.5", "tokens": 1000, "cost": 0.002, "status": "success"},
    {"timestamp": "2024-01-15 10:45", "model": "gpt-4", "tokens": 3000, "cost": 0.09, "status": "success"},
]

df = pd.DataFrame(usage_data)
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Analysis
print("=== API Usage Report ===\n")

# Total stats
print(f"Total requests: {len(df)}")
print(f"Total tokens: {df['tokens'].sum():,}")
print(f"Total cost: ${df['cost'].sum():.4f}")
print(f"Success rate: {(df['status'] == 'success').mean() * 100:.1f}%\n")

# Per-model breakdown
model_stats = df.groupby("model").agg({
    "tokens": ["sum", "mean"],
    "cost": ["sum", "mean"],
    "status": lambda x: (x == "success").sum()
}).round(4)
model_stats.columns = ["total_tokens", "avg_tokens", "total_cost", "avg_cost", "successes"]
print("Per-model breakdown:")
print(model_stats)

# Most expensive request
expensive = df.loc[df["cost"].idxmax()]
print(f"\nMost expensive request: {expensive['model']} - ${expensive['cost']:.4f} ({expensive['tokens']} tokens)")

# Error analysis
errors = df[df["status"] == "error"]
if len(errors) > 0:
    print(f"\n{len(errors)} errors found:")
    for _, err in errors.iterrows():
        print(f"  {err['timestamp']} - {err['model']} - {err['tokens']} tokens")
```

---

## 9. Exercises

### Exercise 1: Log Analyzer
```python
# Create a DataFrame from this log data and analyze:
# 1. Count entries by log level
# 2. Find the busiest hour
# 3. List all unique error messages
# 4. Calculate average time between entries
```

### Exercise 2: Model Comparison Dashboard
```python
# Given a CSV-like dataset of AI model benchmarks:
# model, benchmark, score, date
# Create analysis showing:
# 1. Average score per model across benchmarks
# 2. Best model per benchmark
# 3. Score improvement over time
# 4. Export summary to JSON
```

### Exercise 3: Cost Forecaster
```python
# Using the usage data from the practical:
# 1. Calculate daily average cost
# 2. Project monthly cost at current usage rate
# 3. Identify the most cost-effective model (score/cost ratio)
# 4. Recommend which model to use for budget optimization
```

---

## Solutions

See [solutions/day19_solutions.py](../solutions/day19_solutions.py)

---

## Key Takeaways
- Pandas `DataFrame` is the core structure for tabular data
- Filter with boolean indexing: `df[df["col"] > value]`
- Transform with `.apply()` and column operations
- Aggregate with `.groupby().agg()`
- Data analysis is essential for AI agent logging, monitoring, and optimization

**Tomorrow:** Async Python & concurrency →
