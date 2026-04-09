# Day 20: Async Python & Concurrency

## Learning Goals
- Understand synchronous vs asynchronous execution
- Use `async`/`await` syntax
- Run concurrent API calls with `asyncio`
- Apply async patterns to AI agent workflows

---

## 1. The Problem: Blocking I/O

```python
import time

def call_api_sync(prompt: str) -> str:
    """Simulate a slow API call (1 second)."""
    time.sleep(1)
    return f"Response to: {prompt}"

# Sequential: 5 calls = 5 seconds
start = time.time()
results = []
for i in range(5):
    result = call_api_sync(f"Question {i}")
    results.append(result)
print(f"Sequential: {time.time() - start:.1f}s")  # ~5.0s
```

---

## 2. Async Basics

```python
import asyncio

async def call_api_async(prompt: str) -> str:
    """Simulate a slow API call asynchronously."""
    await asyncio.sleep(1)  # Non-blocking sleep
    return f"Response to: {prompt}"

async def main():
    # Concurrent: 5 calls = ~1 second!
    tasks = [call_api_async(f"Question {i}") for i in range(5)]
    results = await asyncio.gather(*tasks)
    for r in results:
        print(r)

# Run it
asyncio.run(main())
```

### Key Concepts
```python
# async def — defines a coroutine (async function)
async def my_function():
    pass

# await — pauses execution until the awaitable completes
result = await some_async_operation()

# asyncio.gather() — run multiple coroutines concurrently
results = await asyncio.gather(task1, task2, task3)

# asyncio.run() — entry point to run async code
asyncio.run(main())
```

---

## 3. Real-World: Concurrent API Calls

```python
import asyncio
import time

async def call_llm(prompt: str, model: str, delay: float = 0.5) -> dict:
    """Simulate an LLM API call."""
    await asyncio.sleep(delay)  # Simulate network latency
    return {
        "model": model,
        "prompt": prompt[:30],
        "response": f"[{model}] Answer to: {prompt[:20]}...",
        "tokens": len(prompt.split()) * 4
    }

async def multi_model_query(prompt: str) -> list[dict]:
    """Send the same prompt to multiple models concurrently."""
    models = ["gpt-4", "claude-3", "gemini"]
    
    tasks = [call_llm(prompt, model) for model in models]
    results = await asyncio.gather(*tasks)
    
    return results

async def main():
    start = time.time()
    
    prompt = "Explain the benefits of Infrastructure as Code for modern DevOps teams"
    results = await multi_model_query(prompt)
    
    elapsed = time.time() - start
    print(f"Got {len(results)} responses in {elapsed:.2f}s\n")
    
    for r in results:
        print(f"  {r['model']}: {r['response']}")

asyncio.run(main())
```

---

## 4. Error Handling in Async

```python
import asyncio
import random

async def unreliable_api(prompt: str) -> str:
    """Simulate an unreliable API."""
    await asyncio.sleep(random.uniform(0.1, 0.5))
    
    if random.random() < 0.3:
        raise ConnectionError("API connection failed")
    
    return f"Success: {prompt[:20]}..."

async def safe_api_call(prompt: str, retries: int = 3) -> str | None:
    """Call API with retry logic."""
    for attempt in range(1, retries + 1):
        try:
            return await unreliable_api(prompt)
        except ConnectionError as e:
            print(f"  Attempt {attempt} failed: {e}")
            if attempt < retries:
                await asyncio.sleep(0.5 * attempt)
    return None

async def batch_process(prompts: list[str]) -> list[str | None]:
    """Process multiple prompts with individual error handling."""
    tasks = [safe_api_call(prompt) for prompt in prompts]
    results = await asyncio.gather(*tasks)
    return results

async def main():
    prompts = [f"Question about topic {i}" for i in range(10)]
    results = await batch_process(prompts)
    
    successes = sum(1 for r in results if r is not None)
    print(f"\nResults: {successes}/{len(prompts)} successful")

asyncio.run(main())
```

---

## 5. Async with Rate Limiting

```python
import asyncio
import time

class RateLimiter:
    """Limit concurrent API calls."""
    
    def __init__(self, max_concurrent: int = 3, delay: float = 0.1):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.delay = delay
    
    async def execute(self, coro):
        async with self.semaphore:
            result = await coro
            await asyncio.sleep(self.delay)
            return result

async def api_call(prompt_id: int) -> str:
    """Simulate API call."""
    print(f"  Calling API for prompt {prompt_id}...")
    await asyncio.sleep(0.5)
    return f"Result {prompt_id}"

async def main():
    limiter = RateLimiter(max_concurrent=3, delay=0.2)
    
    start = time.time()
    
    tasks = [
        limiter.execute(api_call(i))
        for i in range(10)
    ]
    results = await asyncio.gather(*tasks)
    
    elapsed = time.time() - start
    print(f"\n{len(results)} calls completed in {elapsed:.1f}s")
    print(f"(Sequential would take ~{len(results) * 0.5:.0f}s)")

asyncio.run(main())
```

---

## 6. Async LLM Clients

All three providers support async clients:

### OpenAI (AsyncOpenAI)
```python
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

async def main():
    client = AsyncOpenAI()
    
    prompts = ["What is Docker?", "What is Kubernetes?", "What is Terraform?"]
    
    async def get_answer(prompt: str) -> dict:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Be concise. One sentence."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=50
        )
        return {"prompt": prompt, "answer": response.choices[0].message.content}
    
    results = await asyncio.gather(*[get_answer(p) for p in prompts])
    for r in results:
        print(f"Q: {r['prompt']}\nA: {r['answer']}\n")

asyncio.run(main())
```

### Anthropic (AsyncAnthropic)
```python
import asyncio
import anthropic
from dotenv import load_dotenv

load_dotenv()

async def main():
    client = anthropic.AsyncAnthropic()
    
    prompts = ["What is Docker?", "What is Kubernetes?", "What is Terraform?"]
    
    async def get_answer(prompt: str) -> dict:
        response = await client.messages.create(
            model="claude-sonnet-4-20250514", max_tokens=50,
            system="Be concise. One sentence.",
            messages=[{"role": "user", "content": prompt}]
        )
        return {"prompt": prompt, "answer": response.content[0].text}
    
    results = await asyncio.gather(*[get_answer(p) for p in prompts])
    for r in results:
        print(f"Q: {r['prompt']}\nA: {r['answer']}\n")

asyncio.run(main())
```

### Gemini (async generate)
```python
import asyncio
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure()

async def main():
    model = genai.GenerativeModel("gemini-2.0-flash")
    
    prompts = ["What is Docker?", "What is Kubernetes?", "What is Terraform?"]
    
    async def get_answer(prompt: str) -> dict:
        response = await model.generate_content_async(prompt)
        return {"prompt": prompt, "answer": response.text}
    
    results = await asyncio.gather(*[get_answer(p) for p in prompts])
    for r in results:
        print(f"Q: {r['prompt']}\nA: {r['answer']}\n")

asyncio.run(main())
```

---

## 7. Exercises

### Exercise 1: Parallel Web Checker
```python
# Build an async function that checks multiple URLs concurrently:
# 1. Takes a list of URLs
# 2. Makes async HTTP requests to each
# 3. Returns status, response time, and content length for each
# 4. Limits concurrent connections to 5
# Use aiohttp or httpx for async HTTP
# pip install httpx
```

### Exercise 2: Async Batch Processor
```python
# Build an async batch processor that:
# 1. Reads a list of prompts
# 2. Processes them concurrently in batches of 3
# 3. Implements retry logic per-prompt
# 4. Collects results and errors separately
# 5. Prints a summary: successes, failures, total time
```

### Exercise 3: Agent Pipeline
```python
# Build an async agent pipeline:
# 1. Stage 1: Classify the user's request (async)
# 2. Stage 2: Based on classification, call the right tool (async)
# 3. Stage 3: Format the response (async)
# Each stage should be an async function
# Process 5 different requests through the pipeline concurrently
```

---

## Solutions

See [solutions/day20_solutions.py](../solutions/day20_solutions.py)

---

## Key Takeaways
- `async`/`await` enables concurrent I/O operations
- `asyncio.gather()` runs multiple coroutines concurrently
- Async is perfect for API calls, file I/O, and network operations
- Use `asyncio.Semaphore` for rate limiting
- OpenAI provides `AsyncOpenAI`, Anthropic has `AsyncAnthropic`, and Gemini supports `generate_content_async`
- Handle errors per-task so one failure doesn't crash everything

**Tomorrow:** Mini-Project — AI-Powered Q&A Bot →
