# ============================================
# Day 20 Solutions — Async Python
# ============================================

import asyncio
import time
import random


# --- Exercise 1: Async API Caller ---
print("--- Async API Caller ---")


async def simulate_api_call(model: str, prompt: str, delay: float | None = None) -> dict:
    """Simulate an async API call with variable latency."""
    latency = delay or random.uniform(0.5, 2.0)
    await asyncio.sleep(latency)
    return {
        "model": model,
        "prompt": prompt[:30],
        "response": f"[{model}] Answer to: {prompt[:20]}...",
        "latency": round(latency, 2),
        "tokens": random.randint(50, 500),
    }


async def run_parallel_calls():
    """Run multiple API calls in parallel."""
    prompts = [
        ("gpt-4o-mini", "Explain Docker"),
        ("claude-sonnet", "Explain Kubernetes"),
        ("gemini-flash", "What is CI/CD?"),
        ("gpt-4o-mini", "Explain Terraform"),
        ("claude-sonnet", "What is Python?"),
    ]

    # Sequential
    start = time.time()
    sequential_results = []
    for model, prompt in prompts:
        result = await simulate_api_call(model, prompt, delay=0.5)
        sequential_results.append(result)
    seq_time = time.time() - start

    # Parallel
    start = time.time()
    tasks = [simulate_api_call(model, prompt, delay=0.5) for model, prompt in prompts]
    parallel_results = await asyncio.gather(*tasks)
    par_time = time.time() - start

    print(f"  Sequential: {seq_time:.2f}s")
    print(f"  Parallel:   {par_time:.2f}s")
    print(f"  Speedup:    {seq_time/par_time:.1f}x")

    for r in parallel_results:
        print(f"    {r['model']}: {r['response']} ({r['latency']}s)")


asyncio.run(run_parallel_calls())


# --- Exercise 2: Rate Limiter ---
print("\n--- Rate Limiter ---")


class AsyncRateLimiter:
    """Token-bucket rate limiter for async operations."""

    def __init__(self, max_concurrent: int = 3, delay_between: float = 0.5):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.delay = delay_between
        self.call_count = 0
        self.lock = asyncio.Lock()

    async def execute(self, coro):
        """Execute a coroutine with rate limiting."""
        async with self.semaphore:
            async with self.lock:
                self.call_count += 1
                call_num = self.call_count

            start = time.time()
            result = await coro
            elapsed = time.time() - start

            # Enforce minimum delay
            if elapsed < self.delay:
                await asyncio.sleep(self.delay - elapsed)

            return {"call": call_num, "elapsed": round(elapsed, 2), "result": result}


async def run_rate_limited():
    limiter = AsyncRateLimiter(max_concurrent=2, delay_between=0.3)

    async def mock_api(name: str) -> str:
        await asyncio.sleep(random.uniform(0.1, 0.5))
        return f"Response for {name}"

    tasks = [
        limiter.execute(mock_api(f"request-{i}"))
        for i in range(6)
    ]

    start = time.time()
    results = await asyncio.gather(*tasks)
    total_time = time.time() - start

    for r in results:
        print(f"  Call {r['call']}: {r['result']['result']} ({r['elapsed']}s)")
    print(f"  Total time: {total_time:.2f}s (rate-limited)")


asyncio.run(run_rate_limited())


# --- Exercise 3: Async Pipeline ---
print("\n--- Async Pipeline ---")


async def fetch_data(source: str) -> dict:
    """Stage 1: Fetch data."""
    await asyncio.sleep(random.uniform(0.2, 0.5))
    return {"source": source, "raw_data": f"Raw content from {source}", "size": random.randint(100, 1000)}


async def process_data(data: dict) -> dict:
    """Stage 2: Process fetched data."""
    await asyncio.sleep(random.uniform(0.1, 0.3))
    return {
        **data,
        "processed": True,
        "tokens": data["size"] // 4,
        "summary": f"Processed: {data['raw_data'][:30]}",
    }


async def analyze_data(data: dict) -> dict:
    """Stage 3: Analyze processed data."""
    await asyncio.sleep(random.uniform(0.1, 0.2))
    return {
        **data,
        "analyzed": True,
        "sentiment": random.choice(["positive", "neutral", "negative"]),
        "importance": random.randint(1, 10),
    }


async def run_pipeline():
    sources = ["docs/api.md", "logs/server.log", "config/deploy.yaml", "data/metrics.json"]

    start = time.time()

    # Stage 1: Fetch all in parallel
    fetch_tasks = [fetch_data(s) for s in sources]
    fetched = await asyncio.gather(*fetch_tasks)
    print(f"  Stage 1 (fetch):   {time.time() - start:.2f}s")

    # Stage 2: Process all in parallel
    t2 = time.time()
    process_tasks = [process_data(d) for d in fetched]
    processed = await asyncio.gather(*process_tasks)
    print(f"  Stage 2 (process): {time.time() - t2:.2f}s")

    # Stage 3: Analyze all in parallel
    t3 = time.time()
    analyze_tasks = [analyze_data(d) for d in processed]
    analyzed = await asyncio.gather(*analyze_tasks)
    print(f"  Stage 3 (analyze): {time.time() - t3:.2f}s")

    total = time.time() - start
    print(f"  Total pipeline:    {total:.2f}s\n")

    # Report
    for item in analyzed:
        print(f"  {item['source']}: {item['tokens']} tokens, "
              f"sentiment={item['sentiment']}, importance={item['importance']}")


asyncio.run(run_pipeline())
