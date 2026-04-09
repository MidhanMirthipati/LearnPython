# ============================================
# Day 17 Solutions — LLM API Basics (OpenAI, Anthropic, Gemini)
# ============================================
# NOTE: Requires at least one API key in .env file:
#       OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY
#       Falls back to simulated responses if no key

import os
import json
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# --- Provider Detection ---
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "openai")

HAS_OPENAI = False
HAS_ANTHROPIC = False
HAS_GEMINI = False

try:
    from openai import OpenAI
    HAS_OPENAI = bool(os.environ.get("OPENAI_API_KEY"))
except ImportError:
    pass

try:
    import anthropic
    HAS_ANTHROPIC = bool(os.environ.get("ANTHROPIC_API_KEY"))
except ImportError:
    pass

try:
    import google.generativeai as genai
    HAS_GEMINI = bool(os.environ.get("GOOGLE_API_KEY"))
    if HAS_GEMINI:
        genai.configure()
except ImportError:
    pass

# Auto-select provider based on available keys
if LLM_PROVIDER == "openai" and HAS_OPENAI:
    client = OpenAI()
    active_provider = "openai"
elif LLM_PROVIDER == "anthropic" and HAS_ANTHROPIC:
    client = anthropic.Anthropic()
    active_provider = "anthropic"
elif LLM_PROVIDER == "gemini" and HAS_GEMINI:
    client = genai.GenerativeModel("gemini-2.0-flash")
    active_provider = "gemini"
elif HAS_OPENAI:
    client = OpenAI()
    active_provider = "openai"
elif HAS_ANTHROPIC:
    client = anthropic.Anthropic()
    active_provider = "anthropic"
elif HAS_GEMINI:
    client = genai.GenerativeModel("gemini-2.0-flash")
    active_provider = "gemini"
else:
    client = None
    active_provider = "simulated"
    print("[INFO] No LLM API key found. Using simulated responses.\n")

DEFAULT_MODELS = {"openai": "gpt-4o-mini", "anthropic": "claude-sonnet-4-20250514", "gemini": "gemini-2.0-flash"}


def call_llm(messages: list[dict], model: str = None,
             temperature: float = 0.7, max_tokens: int = 300) -> dict:
    """Call the active LLM provider or simulate."""
    model = model or DEFAULT_MODELS.get(active_provider, "gpt-4o-mini")

    if active_provider == "openai":
        response = client.chat.completions.create(
            model=model, messages=messages,
            temperature=temperature, max_tokens=max_tokens,
        )
        return {
            "content": response.choices[0].message.content,
            "model": response.model,
            "tokens": response.usage.total_tokens,
        }
    elif active_provider == "anthropic":
        system_msg = next((m["content"] for m in messages if m["role"] == "system"), "")
        api_messages = [m for m in messages if m["role"] != "system"]
        response = client.messages.create(
            model=model, system=system_msg,
            messages=api_messages,
            temperature=temperature, max_tokens=max_tokens,
        )
        return {
            "content": response.content[0].text,
            "model": model,
            "tokens": response.usage.input_tokens + response.usage.output_tokens,
        }
    elif active_provider == "gemini":
        prompt = "\n".join(f"{m['role']}: {m['content']}" for m in messages)
        response = client.generate_content(
            prompt,
            generation_config={"temperature": temperature, "max_output_tokens": max_tokens},
        )
        return {
            "content": response.text,
            "model": model,
            "tokens": response.usage_metadata.total_token_count if response.usage_metadata else 0,
        }
    else:
        user_msg = messages[-1]["content"] if messages else ""
        return {
            "content": f"[Simulated] Response to: {user_msg[:80]}...",
            "model": model,
            "tokens": len(user_msg.split()) * 3,
        }

print(f"[INFO] Active provider: {active_provider}")


# --- Exercise 1: Multi-Turn Conversation ---
print("--- Multi-Turn Conversation ---")

conversation = [
    {"role": "system", "content": "You are a helpful DevOps assistant. Be concise."},
]

test_messages = [
    "What is Docker?",
    "How is it different from a VM?",
    "Give me a simple Dockerfile example",
]

for msg in test_messages:
    conversation.append({"role": "user", "content": msg})
    result = call_llm(conversation)
    conversation.append({"role": "assistant", "content": result["content"]})
    
    print(f"\nUser: {msg}")
    print(f"Assistant: {result['content'][:150]}...")
    print(f"  [{result['tokens']} tokens]")


# --- Exercise 2: Temperature Comparison ---
print("\n\n--- Temperature Comparison ---")

prompt = "Write a one-sentence creative tagline for an AI-powered DevOps tool."
temperatures = [0.0, 0.5, 1.0]

for temp in temperatures:
    messages = [
        {"role": "system", "content": "You are a creative marketing writer."},
        {"role": "user", "content": prompt},
    ]
    result = call_llm(messages, temperature=temp, max_tokens=60)
    print(f"\n  Temperature {temp}:")
    print(f"    {result['content']}")


# --- Exercise 3: Structured Output ---
print("\n\n--- Structured Output ---")

structured_prompt = """Analyze the following error log and return a JSON response with these fields:
- severity: "low", "medium", "high", or "critical"
- category: the type of error
- summary: one-sentence summary
- suggested_fix: one-sentence fix suggestion

Error log:
```
2024-01-15 08:15:33 ERROR [database] Connection pool exhausted. 
Active connections: 100/100. Queue timeout after 30s. 
Service: user-auth. Affected users: ~2000.
```

Respond with ONLY valid JSON, no other text."""

messages = [
    {"role": "system", "content": "You are a log analysis expert. Always respond in valid JSON."},
    {"role": "user", "content": structured_prompt},
]

result = call_llm(messages, temperature=0.0, max_tokens=200)
print(f"Raw response: {result['content'][:200]}")

# Parse the response
try:
    parsed = json.loads(result["content"])
    print(f"\nParsed analysis:")
    for key, value in parsed.items():
        print(f"  {key}: {value}")
except json.JSONDecodeError:
    print(f"\n  Could not parse as JSON — model response was not valid JSON")
    print(f"  Response: {result['content'][:200]}")
