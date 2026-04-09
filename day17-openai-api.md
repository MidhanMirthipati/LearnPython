# Day 17: Calling LLM APIs (OpenAI, Anthropic, Gemini)

## Learning Goals
- Set up Python clients for **OpenAI**, **Anthropic (Claude)**, and **Google Gemini**
- Make chat completion requests with all three providers
- Handle streaming responses  
- Manage conversation context
- Build a provider-agnostic wrapper

---

## 1. Setup

```bash
pip install openai anthropic google-generativeai python-dotenv
```

Create your `.env` file:
```ini
# Add the keys for providers you want to use (you need at least one)
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
GOOGLE_API_KEY=your-google-key-here
```

> **Getting API keys:**
> - **OpenAI:** [platform.openai.com/api-keys](https://platform.openai.com/api-keys) — create account, add payment method ($5 min)
> - **Anthropic:** [console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys) — create account, add credits
> - **Google Gemini:** [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) — free tier available, no credit card needed

---

## 2. Your First API Call — All Three Providers

### OpenAI
```python
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()  # Reads OPENAI_API_KEY from environment

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful DevOps assistant."},
        {"role": "user", "content": "What is Docker in one sentence?"}
    ],
    temperature=0.7,
    max_tokens=100
)

answer = response.choices[0].message.content
print(answer)
print(f"Tokens used: {response.usage.total_tokens}")
```

### Anthropic (Claude)
```python
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()  # Reads ANTHROPIC_API_KEY from environment

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=100,
    system="You are a helpful DevOps assistant.",  # system is a top-level param
    messages=[
        {"role": "user", "content": "What is Docker in one sentence?"}
    ],
    temperature=0.7
)

answer = response.content[0].text
print(answer)
print(f"Tokens used: {response.usage.input_tokens + response.usage.output_tokens}")
```

### Google Gemini
```python
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure()  # Reads GOOGLE_API_KEY from environment

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    system_instruction="You are a helpful DevOps assistant."
)

response = model.generate_content(
    "What is Docker in one sentence?",
    generation_config=genai.GenerationConfig(
        temperature=0.7,
        max_output_tokens=100
    )
)

print(response.text)
print(f"Tokens used: {response.usage_metadata.total_token_count}")
```

---

## 3. Key Differences Between Providers

| Feature | OpenAI | Anthropic (Claude) | Google Gemini |
|---------|--------|-------------------|---------------|
| **SDK** | `openai` | `anthropic` | `google-generativeai` |
| **Client** | `OpenAI()` | `anthropic.Anthropic()` | `genai.GenerativeModel()` |
| **Models** | `gpt-4o-mini`, `gpt-4o` | `claude-sonnet-4-20250514`, `claude-haiku-4-20250514` | `gemini-2.0-flash`, `gemini-2.5-pro` |
| **System prompt** | In `messages` array | Top-level `system=` param | `system_instruction=` on model |
| **Response text** | `.choices[0].message.content` | `.content[0].text` | `.text` |
| **Token usage** | `.usage.total_tokens` | `.usage.input_tokens + .usage.output_tokens` | `.usage_metadata.total_token_count` |
| **API key env var** | `OPENAI_API_KEY` | `ANTHROPIC_API_KEY` | `GOOGLE_API_KEY` |

---

## 4. Multi-turn Conversations

### OpenAI
```python
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

messages = [
    {"role": "system", "content": "You are a DevOps expert. Be concise."}
]

def chat_openai(user_message: str) -> str:
    messages.append({"role": "user", "content": user_message})
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
        max_tokens=500
    )
    assistant_message = response.choices[0].message.content
    messages.append({"role": "assistant", "content": assistant_message})
    return assistant_message

print(chat_openai("What is Kubernetes?"))
print(chat_openai("How does it differ from Docker?"))
print(chat_openai("Give me a simple YAML example."))
```

### Anthropic (Claude)
```python
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

messages = []

def chat_anthropic(user_message: str) -> str:
    messages.append({"role": "user", "content": user_message})
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        system="You are a DevOps expert. Be concise.",
        messages=messages,
        temperature=0.7
    )
    assistant_message = response.content[0].text
    messages.append({"role": "assistant", "content": assistant_message})
    return assistant_message

print(chat_anthropic("What is Kubernetes?"))
print(chat_anthropic("How does it differ from Docker?"))
print(chat_anthropic("Give me a simple YAML example."))
```

### Google Gemini
```python
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure()

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    system_instruction="You are a DevOps expert. Be concise."
)
chat = model.start_chat()  # Maintains conversation history automatically

def chat_gemini(user_message: str) -> str:
    response = chat.send_message(user_message)
    return response.text

print(chat_gemini("What is Kubernetes?"))
print(chat_gemini("How does it differ from Docker?"))
print(chat_gemini("Give me a simple YAML example."))
```

---

## 5. Streaming Responses

### OpenAI
```python
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

stream = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain CI/CD in 3 bullet points"}
    ],
    stream=True
)

for chunk in stream:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
print()
```

### Anthropic (Claude)
```python
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

with client.messages.stream(
    model="claude-sonnet-4-20250514",
    max_tokens=500,
    system="You are a helpful assistant.",
    messages=[{"role": "user", "content": "Explain CI/CD in 3 bullet points"}]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
print()
```

### Google Gemini
```python
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure()

model = genai.GenerativeModel("gemini-2.0-flash")

response = model.generate_content(
    "Explain CI/CD in 3 bullet points",
    stream=True
)

for chunk in response:
    print(chunk.text, end="", flush=True)
print()
```

---

## 6. Error Handling for API Calls

Each provider has its own error types. Here's how to handle them:

### OpenAI
```python
from openai import OpenAI, APIError, RateLimitError, APIConnectionError
from dotenv import load_dotenv
import time

load_dotenv()
client = OpenAI()

def safe_chat_openai(messages: list[dict], retries: int = 3) -> str | None:
    for attempt in range(1, retries + 1):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except RateLimitError:
            wait = 2 ** attempt
            print(f"Rate limited. Waiting {wait}s... (attempt {attempt})")
            time.sleep(wait)
        except APIConnectionError:
            print(f"Connection error. Retrying... (attempt {attempt})")
            time.sleep(2)
        except APIError as e:
            print(f"API error: {e}")
            if e.status_code and e.status_code >= 500:
                time.sleep(2)
            else:
                return None
    return None
```

### Anthropic (Claude)
```python
import anthropic
from dotenv import load_dotenv
import time

load_dotenv()
client = anthropic.Anthropic()

def safe_chat_anthropic(messages: list[dict], retries: int = 3) -> str | None:
    for attempt in range(1, retries + 1):
        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                messages=messages,
                temperature=0.7
            )
            return response.content[0].text
        except anthropic.RateLimitError:
            wait = 2 ** attempt
            print(f"Rate limited. Waiting {wait}s... (attempt {attempt})")
            time.sleep(wait)
        except anthropic.APIConnectionError:
            print(f"Connection error. Retrying... (attempt {attempt})")
            time.sleep(2)
        except anthropic.APIError as e:
            print(f"API error: {e}")
            return None
    return None
```

### Google Gemini
```python
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
from dotenv import load_dotenv
import time

load_dotenv()
genai.configure()
model = genai.GenerativeModel("gemini-2.0-flash")

def safe_chat_gemini(prompt: str, retries: int = 3) -> str | None:
    for attempt in range(1, retries + 1):
        try:
            response = model.generate_content(prompt)
            return response.text
        except google_exceptions.ResourceExhausted:
            wait = 2 ** attempt
            print(f"Rate limited. Waiting {wait}s... (attempt {attempt})")
            time.sleep(wait)
        except google_exceptions.ServiceUnavailable:
            print(f"Service unavailable. Retrying... (attempt {attempt})")
            time.sleep(2)
        except Exception as e:
            print(f"Error: {e}")
            return None
    return None
```

---

## 7. Practical: Provider-Agnostic Chat Application

```python
from dotenv import load_dotenv
import json
import os

load_dotenv()


class ChatApp:
    """A chat app that works with OpenAI, Anthropic, or Gemini."""

    def __init__(self, system_prompt: str, provider: str = "openai", model: str = None):
        self.provider = provider
        self.system_prompt = system_prompt
        self.messages = []
        self.total_tokens = 0

        if provider == "openai":
            from openai import OpenAI
            self.client = OpenAI()
            self.model = model or "gpt-4o-mini"
        elif provider == "anthropic":
            import anthropic
            self.client = anthropic.Anthropic()
            self.model = model or "claude-sonnet-4-20250514"
        elif provider == "gemini":
            import google.generativeai as genai
            genai.configure()
            self._genai_model = genai.GenerativeModel(
                model_name=model or "gemini-2.0-flash",
                system_instruction=system_prompt
            )
            self._chat = self._genai_model.start_chat()
            self.model = model or "gemini-2.0-flash"
        else:
            raise ValueError(f"Unknown provider: {provider}. Use 'openai', 'anthropic', or 'gemini'.")

    def chat(self, user_message: str) -> str:
        self.messages.append({"role": "user", "content": user_message})

        if self.provider == "openai":
            api_messages = [{"role": "system", "content": self.system_prompt}] + self.messages
            response = self.client.chat.completions.create(
                model=self.model, messages=api_messages, temperature=0.7, max_tokens=1000
            )
            content = response.choices[0].message.content
            self.total_tokens += response.usage.total_tokens

        elif self.provider == "anthropic":
            response = self.client.messages.create(
                model=self.model, max_tokens=1000, system=self.system_prompt,
                messages=self.messages, temperature=0.7
            )
            content = response.content[0].text
            self.total_tokens += response.usage.input_tokens + response.usage.output_tokens

        elif self.provider == "gemini":
            response = self._chat.send_message(user_message)
            content = response.text
            self.total_tokens += response.usage_metadata.total_token_count

        self.messages.append({"role": "assistant", "content": content})
        return content

    def get_stats(self) -> dict:
        return {
            "provider": self.provider,
            "model": self.model,
            "messages": len(self.messages),
            "total_tokens": self.total_tokens,
        }

    def run(self):
        print(f"Chat started with {self.provider}/{self.model}. Type 'quit' to exit.\n")
        while True:
            user_input = input("You: ").strip()
            if not user_input:
                continue
            if user_input.lower() == "quit":
                print(f"\nSession stats: {json.dumps(self.get_stats(), indent=2)}")
                break
            response = self.chat(user_input)
            print(f"\nAssistant: {response}\n")


if __name__ == "__main__":
    # Change provider to "anthropic" or "gemini" to switch
    provider = os.environ.get("LLM_PROVIDER", "openai")
    app = ChatApp(
        system_prompt="You are an expert DevOps engineer. Be concise and practical.",
        provider=provider
    )
    app.run()
```

---

## 8. Exercises

### Exercise 1: Provider Comparison Tool
```python
# Build a script that sends the SAME prompt to all 3 providers and compares:
# 1. Send a DevOps question to OpenAI (gpt-4o-mini), Anthropic (claude-sonnet-4-20250514), Gemini (gemini-2.0-flash)
# 2. Compare response quality, length, and token usage
# 3. Print a side-by-side comparison table
# Handle the case where a provider key is not configured (skip gracefully)
```

### Exercise 2: Conversation Saver
```python
# Extend the ChatApp with:
# 1. save_conversation(filepath) — save messages to JSON (include provider info)
# 2. load_conversation(filepath) — restore from JSON and continue chatting
# 3. Auto-save every 5 messages
```

### Exercise 3: Batch Processor
```python
# Build a tool that:
# 1. Reads a list of questions from a file (one per line)
# 2. Sends each to the configured LLM provider
# 3. Saves responses to a JSON file with question-answer pairs
# 4. Tracks total tokens used
# 5. Handles rate limits gracefully
# Support all 3 providers via a --provider CLI argument
```

---

## Solutions

See [solutions/day17_solutions.py](../solutions/day17_solutions.py)

---

## Key Takeaways
- **OpenAI**, **Anthropic**, and **Google Gemini** all follow similar patterns: create a client, send messages, get a response
- Each provider has slightly different SDK patterns — learn the differences early
- System prompts are set differently: OpenAI uses `messages`, Anthropic uses a `system=` param, Gemini uses `system_instruction=`
- Streaming syntax varies but the concept is the same across all providers
- Always handle rate limits and errors — each SDK has its own exception types
- Build provider-agnostic wrappers to make switching easy
- Set `LLM_PROVIDER` in `.env` to switch between providers without changing code

**Tomorrow:** Prompt engineering in code →
