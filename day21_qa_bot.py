# ============================================
# Day 21 Solution — AI-Powered Q&A Bot
# ============================================
# Supports OpenAI, Anthropic, and Google Gemini.
# Set LLM_PROVIDER in .env (openai | anthropic | gemini).
# Falls back to simulated responses if no API key is found.
# pip install openai anthropic google-generativeai python-dotenv

import json
import os
from datetime import datetime
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# --- Provider availability ---
try:
    from openai import OpenAI
    HAS_OPENAI = bool(os.environ.get("OPENAI_API_KEY"))
except ImportError:
    HAS_OPENAI = False

try:
    import anthropic
    HAS_ANTHROPIC = bool(os.environ.get("ANTHROPIC_API_KEY"))
except ImportError:
    HAS_ANTHROPIC = False

try:
    import google.generativeai as genai
    HAS_GEMINI = bool(os.environ.get("GOOGLE_API_KEY"))
    if HAS_GEMINI:
        genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
except ImportError:
    HAS_GEMINI = False

LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "openai").lower()
HAS_API = (LLM_PROVIDER == "openai" and HAS_OPENAI) or \
          (LLM_PROVIDER == "anthropic" and HAS_ANTHROPIC) or \
          (LLM_PROVIDER == "gemini" and HAS_GEMINI)


# --- System Prompt Presets ---
SYSTEM_PRESETS = {
    "devops": "You are a senior DevOps engineer with expertise in Docker, Kubernetes, CI/CD, Terraform, and cloud platforms. Be concise and practical. Include command examples when relevant.",
    "python": "You are an expert Python developer and teacher. Explain concepts clearly with code examples. Focus on best practices and Pythonic patterns.",
    "general": "You are a helpful, friendly assistant. Provide clear, accurate answers.",
    "architect": "You are a cloud solutions architect. Focus on scalability, cost optimization, reliability, and security. Use diagrams described in text when helpful.",
}

# --- Model Pricing (per 1K tokens, approximate) ---
MODEL_PRICING = {
    # OpenAI
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-4": {"input": 0.03, "output": 0.06},
    # Anthropic
    "claude-sonnet-4-20250514": {"input": 0.003, "output": 0.015},
    "claude-haiku-4-20250514": {"input": 0.0008, "output": 0.004},
    # Google Gemini
    "gemini-2.0-flash": {"input": 0.000075, "output": 0.0003},
    "gemini-2.5-pro-preview-06-05": {"input": 0.00125, "output": 0.01},
}

# Default models per provider
DEFAULT_MODELS = {
    "openai": "gpt-4o-mini",
    "anthropic": "claude-sonnet-4-20250514",
    "gemini": "gemini-2.0-flash",
}


class ChatEngine:
    """Core chat engine supporting OpenAI, Anthropic, and Gemini."""

    def __init__(self, system_prompt: str, provider: str = LLM_PROVIDER,
                 model: str | None = None):
        self.provider = provider
        self.model = model or DEFAULT_MODELS.get(provider, "gpt-4o-mini")
        self.system_prompt = system_prompt
        self.messages: list[dict] = [{"role": "system", "content": system_prompt}]
        self.total_tokens = 0
        self.total_cost = 0.0
        self.request_count = 0
        self.use_api = HAS_API

        if self.provider == "openai" and HAS_OPENAI:
            self.client = OpenAI()
        elif self.provider == "anthropic" and HAS_ANTHROPIC:
            self.client = anthropic.Anthropic()
        elif self.provider == "gemini" and HAS_GEMINI:
            self.client = genai.GenerativeModel(self.model)
        else:
            self.client = None
            self.use_api = False
            print(f"[INFO] No {provider} API key found. Using simulated responses.")

    def set_model(self, model: str):
        if model in MODEL_PRICING:
            self.model = model
            print(f"  Model switched to: {model}")
        else:
            print(f"  Unknown model. Available: {', '.join(MODEL_PRICING.keys())}")

    def set_system_prompt(self, preset_name: str):
        if preset_name in SYSTEM_PRESETS:
            self.messages[0] = {"role": "system", "content": SYSTEM_PRESETS[preset_name]}
            print(f"  System prompt changed to: {preset_name}")
        else:
            print(f"  Unknown preset. Available: {', '.join(SYSTEM_PRESETS.keys())}")

    def _calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        rate = MODEL_PRICING.get(self.model, {"input": 0.001, "output": 0.002})
        return (prompt_tokens / 1000 * rate["input"] +
                completion_tokens / 1000 * rate["output"])

    def _simulate_response(self, user_message: str) -> dict:
        """Simulated response when no API key is available."""
        response = f"[Simulated {self.provider}/{self.model}] Placeholder response to: '{user_message[:50]}...'. Set {self.provider.upper()} API key in .env for real responses."
        prompt_tokens = sum(len(m["content"].split()) for m in self.messages) * 2
        completion_tokens = len(response.split()) * 2
        return {
            "content": response,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
        }

    def chat(self, user_message: str, stream: bool = True) -> str:
        self.messages.append({"role": "user", "content": user_message})

        if not self.use_api:
            result = self._simulate_response(user_message)
            content = result["content"]
            print(f"\n  Assistant: {content}\n")
        elif stream:
            content = self._stream_response()
        else:
            content = self._normal_response()

        self.messages.append({"role": "assistant", "content": content})
        self.request_count += 1

        if self.use_api:
            # Tokens are tracked from the API response
            pass
        else:
            tokens = result["prompt_tokens"] + result["completion_tokens"]
            cost = self._calculate_cost(result["prompt_tokens"], result["completion_tokens"])
            self.total_tokens += tokens
            self.total_cost += cost
            print(f"  [{tokens} tokens | ${cost:.4f}]")

        return content

    def _stream_response(self) -> str:
        if self.provider == "openai":
            return self._stream_openai()
        elif self.provider == "anthropic":
            return self._stream_anthropic()
        elif self.provider == "gemini":
            return self._stream_gemini()
        return ""

    def _stream_openai(self) -> str:
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            stream=True,
            temperature=0.7,
            max_tokens=1000,
        )

        print("\n  Assistant: ", end="", flush=True)
        full_response = ""
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                print(content, end="", flush=True)
                full_response += content
        print("\n")

        est_prompt = sum(len(m["content"].split()) for m in self.messages) * 2
        est_completion = len(full_response.split()) * 2
        cost = self._calculate_cost(est_prompt, est_completion)
        self.total_tokens += est_prompt + est_completion
        self.total_cost += cost
        print(f"  [~{est_prompt + est_completion} tokens | ~${cost:.4f}]")
        return full_response

    def _stream_anthropic(self) -> str:
        # Anthropic uses system as a separate param, not in messages
        user_msgs = [m for m in self.messages if m["role"] != "system"]
        print("\n  Assistant: ", end="", flush=True)
        full_response = ""
        with self.client.messages.stream(
            model=self.model,
            system=self.system_prompt,
            messages=user_msgs,
            max_tokens=1000,
            temperature=0.7,
        ) as stream:
            for text in stream.text_stream:
                print(text, end="", flush=True)
                full_response += text
        print("\n")

        est_prompt = sum(len(m["content"].split()) for m in self.messages) * 2
        est_completion = len(full_response.split()) * 2
        cost = self._calculate_cost(est_prompt, est_completion)
        self.total_tokens += est_prompt + est_completion
        self.total_cost += cost
        print(f"  [~{est_prompt + est_completion} tokens | ~${cost:.4f}]")
        return full_response

    def _stream_gemini(self) -> str:
        # Gemini uses a different message format
        contents = []
        for m in self.messages:
            if m["role"] == "system":
                continue  # Handled via model system_instruction
            role = "user" if m["role"] == "user" else "model"
            contents.append({"role": role, "parts": [m["content"]]})

        print("\n  Assistant: ", end="", flush=True)
        full_response = ""
        response = self.client.generate_content(contents, stream=True)
        for chunk in response:
            if chunk.text:
                print(chunk.text, end="", flush=True)
                full_response += chunk.text
        print("\n")

        est_prompt = sum(len(m["content"].split()) for m in self.messages) * 2
        est_completion = len(full_response.split()) * 2
        cost = self._calculate_cost(est_prompt, est_completion)
        self.total_tokens += est_prompt + est_completion
        self.total_cost += cost
        print(f"  [~{est_prompt + est_completion} tokens | ~${cost:.4f}]")
        return full_response

        return full_response

    def _normal_response(self) -> str:
        if self.provider == "openai":
            return self._normal_openai()
        elif self.provider == "anthropic":
            return self._normal_anthropic()
        elif self.provider == "gemini":
            return self._normal_gemini()
        return ""

    def _normal_openai(self) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            temperature=0.7,
            max_tokens=1000,
        )

        content = response.choices[0].message.content
        tokens = response.usage.total_tokens
        cost = self._calculate_cost(response.usage.prompt_tokens, response.usage.completion_tokens)

        self.total_tokens += tokens
        self.total_cost += cost

        print(f"\n  Assistant: {content}\n")
        print(f"  [{tokens} tokens | ${cost:.4f}]")

        return content

    def _normal_anthropic(self) -> str:
        user_msgs = [m for m in self.messages if m["role"] != "system"]
        response = self.client.messages.create(
            model=self.model,
            system=self.system_prompt,
            messages=user_msgs,
            max_tokens=1000,
            temperature=0.7,
        )

        content = response.content[0].text
        tokens = response.usage.input_tokens + response.usage.output_tokens
        cost = self._calculate_cost(response.usage.input_tokens, response.usage.output_tokens)

        self.total_tokens += tokens
        self.total_cost += cost

        print(f"\n  Assistant: {content}\n")
        print(f"  [{tokens} tokens | ${cost:.4f}]")

        return content

    def _normal_gemini(self) -> str:
        contents = []
        for m in self.messages:
            if m["role"] == "system":
                continue
            role = "user" if m["role"] == "user" else "model"
            contents.append({"role": role, "parts": [m["content"]]})

        response = self.client.generate_content(contents)

        content = response.text
        # Gemini doesn't always expose token counts the same way
        est_prompt = sum(len(m["content"].split()) for m in self.messages) * 2
        est_completion = len(content.split()) * 2
        tokens = est_prompt + est_completion
        cost = self._calculate_cost(est_prompt, est_completion)

        self.total_tokens += tokens
        self.total_cost += cost

        print(f"\n  Assistant: {content}\n")
        print(f"  [~{tokens} tokens | ~${cost:.4f}]")

        return content

    def clear(self):
        system = self.messages[0]
        self.messages = [system]
        print("  Conversation cleared.")

    def get_stats(self) -> dict:
        return {
            "provider": self.provider,
            "model": self.model,
            "messages": len(self.messages),
            "requests": self.request_count,
            "total_tokens": self.total_tokens,
            "total_cost": f"${self.total_cost:.4f}",
            "api_connected": self.use_api,
        }

    def export_json(self, filepath: str):
        data = {
            "exported_at": datetime.now().isoformat(),
            "model": self.model,
            "stats": self.get_stats(),
            "messages": self.messages,
        }
        Path(filepath).write_text(json.dumps(data, indent=2))
        print(f"  Exported to {filepath}")

    def export_markdown(self, filepath: str):
        lines = [f"# Chat Export — {datetime.now().strftime('%Y-%m-%d %H:%M')}", ""]
        for msg in self.messages:
            role = msg["role"].title()
            lines.append(f"**{role}:** {msg['content']}\n")
        Path(filepath).write_text("\n".join(lines))
        print(f"  Exported to {filepath}")


def show_help():
    print("""
  Commands:
    /help              — Show this help
    /provider [name]   — Switch provider (openai, anthropic, gemini)
    /model [name]      — Switch model (gpt-4o-mini, claude-sonnet-4-20250514, gemini-2.0-flash, etc.)
    /system [preset]   — Change personality (devops, python, general, architect)
    /stats             — Show usage statistics
    /export [path]     — Export conversation to JSON
    /exportmd [path]   — Export conversation to Markdown
    /clear             — Clear conversation history
    /quit              — Exit with stats
    """)


def main():
    print("=" * 50)
    print("  AI-Powered Q&A Bot")
    print("=" * 50)

    # Choose personality
    print("\n  Available personalities:")
    for name, prompt in SYSTEM_PRESETS.items():
        print(f"    {name}: {prompt[:60]}...")
    preset = input("\n  Choose personality (or press Enter for 'devops'): ").strip() or "devops"

    system_prompt = SYSTEM_PRESETS.get(preset, SYSTEM_PRESETS["devops"])
    engine = ChatEngine(system_prompt)

    print(f"\n  Ready! Provider: {engine.provider} | Model: {engine.model} | Personality: {preset}")
    print("  Type /help for commands.\n")

    while True:
        user_input = input("  You: ").strip()

        if not user_input:
            continue

        if user_input.startswith("/"):
            parts = user_input.split(maxsplit=1)
            cmd = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else ""

            if cmd == "/quit":
                stats = engine.get_stats()
                print(f"\n  Session Summary:")
                for k, v in stats.items():
                    print(f"    {k}: {v}")
                print("\n  Goodbye!\n")
                break
            elif cmd == "/help":
                show_help()
            elif cmd == "/provider":
                if arg in ("openai", "anthropic", "gemini"):
                    engine = ChatEngine(system_prompt, provider=arg)
                    print(f"  Switched to {arg} ({engine.model})")
                else:
                    print("  Available providers: openai, anthropic, gemini")
            elif cmd == "/model":
                engine.set_model(arg)
            elif cmd == "/system":
                engine.set_system_prompt(arg)
            elif cmd == "/stats":
                for k, v in engine.get_stats().items():
                    print(f"    {k}: {v}")
            elif cmd == "/export":
                engine.export_json(arg or "chat_export.json")
            elif cmd == "/exportmd":
                engine.export_markdown(arg or "chat_export.md")
            elif cmd == "/clear":
                engine.clear()
            else:
                print(f"  Unknown command: {cmd}")
            continue

        engine.chat(user_input)


if __name__ == "__main__":
    main()
