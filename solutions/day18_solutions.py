# ============================================
# Day 18 Solutions — Prompt Engineering
# ============================================
# Supports OpenAI, Anthropic, and Gemini via LLM_PROVIDER env var

import os
import json

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "openai")
HAS_API = False

try:
    if LLM_PROVIDER == "openai":
        from openai import OpenAI
        if os.environ.get("OPENAI_API_KEY"):
            client = OpenAI()
            HAS_API = True
    elif LLM_PROVIDER == "anthropic":
        import anthropic
        if os.environ.get("ANTHROPIC_API_KEY"):
            client = anthropic.Anthropic()
            HAS_API = True
    elif LLM_PROVIDER == "gemini":
        import google.generativeai as genai
        if os.environ.get("GOOGLE_API_KEY"):
            genai.configure()
            client = genai.GenerativeModel("gemini-2.0-flash")
            HAS_API = True
except ImportError:
    pass

if not HAS_API:
    client = None


def call_llm(messages: list[dict], **kwargs) -> str:
    """Call the configured LLM provider or simulate."""
    if HAS_API and LLM_PROVIDER == "openai":
        resp = client.chat.completions.create(
            model=kwargs.get("model", "gpt-4o-mini"),
            messages=messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 500),
        )
        return resp.choices[0].message.content
    elif HAS_API and LLM_PROVIDER == "anthropic":
        system_msg = next((m["content"] for m in messages if m["role"] == "system"), "")
        api_msgs = [m for m in messages if m["role"] != "system"]
        resp = client.messages.create(
            model=kwargs.get("model", "claude-sonnet-4-20250514"),
            system=system_msg, messages=api_msgs,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 500),
        )
        return resp.content[0].text
    elif HAS_API and LLM_PROVIDER == "gemini":
        prompt = "\n".join(f"{m['role']}: {m['content']}" for m in messages)
        resp = client.generate_content(
            prompt,
            generation_config={"temperature": kwargs.get("temperature", 0.7),
                               "max_output_tokens": kwargs.get("max_tokens", 500)},
        )
        return resp.text
    else:
        return f"[Simulated] Response to: {messages[-1]['content'][:80]}..."


# --- Exercise 1: Prompt Template Library ---
print("--- Prompt Template Library ---")


class PromptTemplate:
    """A reusable prompt template with variables."""

    def __init__(self, name: str, system: str, user_template: str,
                 variables: list[str], output_format: str = "text"):
        self.name = name
        self.system = system
        self.user_template = user_template
        self.variables = variables
        self.output_format = output_format

    def render(self, **kwargs) -> list[dict]:
        """Render the template with given variables."""
        missing = [v for v in self.variables if v not in kwargs]
        if missing:
            raise ValueError(f"Missing variables: {missing}")

        user_content = self.user_template
        for key, value in kwargs.items():
            user_content = user_content.replace(f"{{{{{key}}}}}", str(value))

        if self.output_format == "json":
            user_content += "\n\nRespond with ONLY valid JSON."

        return [
            {"role": "system", "content": self.system},
            {"role": "user", "content": user_content},
        ]


# Create templates
templates = {
    "code_review": PromptTemplate(
        name="code_review",
        system="You are a senior software engineer. Provide constructive code reviews focusing on bugs, performance, and best practices.",
        user_template="Review this {{language}} code:\n```{{language}}\n{{code}}\n```\nFocus on: {{focus}}",
        variables=["language", "code", "focus"],
    ),
    "explain": PromptTemplate(
        name="explain",
        system="You are a patient teacher. Explain concepts at the specified level.",
        user_template="Explain {{topic}} at a {{level}} level. Use {{style}} format.",
        variables=["topic", "level", "style"],
    ),
    "incident": PromptTemplate(
        name="incident",
        system="You are a DevOps incident commander. Analyze errors and provide actionable steps.",
        user_template="Analyze this incident:\nService: {{service}}\nError: {{error}}\nImpact: {{impact}}\n\nProvide: 1) Root cause 2) Immediate fix 3) Prevention",
        variables=["service", "error", "impact"],
        output_format="json",
    ),
}

# Test code review template
messages = templates["code_review"].render(
    language="python",
    code="def get_user(id):\n  data = eval(input())\n  return data[id]",
    focus="security",
)
print(f"Code Review Prompt:\n{json.dumps(messages, indent=2)}\n")
response = call_llm(messages)
print(f"Response: {response[:200]}...\n")


# Test incident template
messages = templates["incident"].render(
    service="payment-service",
    error="Connection refused to database on port 5432",
    impact="All payment processing halted for 500+ users",
)
print(f"Incident Prompt:\n{json.dumps(messages, indent=2)}\n")
response = call_llm(messages, temperature=0.0)
print(f"Response: {response[:200]}...\n")


# --- Exercise 2: Few-Shot Prompt Builder ---
print("\n--- Few-Shot Prompt Builder ---")


def build_few_shot(task_description: str,
                   examples: list[dict],
                   query: str,
                   system: str = "You are a helpful assistant.") -> list[dict]:
    """Build a few-shot prompt from examples."""
    messages = [{"role": "system", "content": system}]

    # Build examples as part of the instruction
    example_text = f"Task: {task_description}\n\nExamples:\n"
    for i, ex in enumerate(examples, 1):
        example_text += f"\nExample {i}:\nInput: {ex['input']}\nOutput: {ex['output']}\n"

    example_text += f"\nNow process this:\nInput: {query}\nOutput:"
    messages.append({"role": "user", "content": example_text})

    return messages


# Sentiment classification with few-shot
examples = [
    {"input": "The deployment went smoothly!", "output": "positive"},
    {"input": "Server crashed again, lost 2 hours of work", "output": "negative"},
    {"input": "Updated the config file", "output": "neutral"},
    {"input": "Great performance improvement after optimization!", "output": "positive"},
]

messages = build_few_shot(
    task_description="Classify the sentiment of DevOps team messages",
    examples=examples,
    query="The new monitoring dashboard is amazing, caught 3 issues before production!",
    system="You are a sentiment classifier. Respond with only: positive, negative, or neutral.",
)

print(f"Few-shot prompt:\n{messages[-1]['content'][:300]}...\n")
response = call_llm(messages, temperature=0.0)
print(f"Classification: {response}\n")


# --- Exercise 3: Chain-of-Thought Analyzer ---
print("\n--- Chain-of-Thought Analyzer ---")


def chain_of_thought(problem: str, context: str = "") -> list[dict]:
    """Build a chain-of-thought prompt."""
    system = """You are an expert problem solver. For each problem:
1. First, restate the problem in your own words
2. Break it down into smaller steps
3. Work through each step with reasoning
4. Arrive at a final answer
5. Double-check your reasoning

Always show your thinking process."""

    user_content = f"Problem: {problem}"
    if context:
        user_content = f"Context: {context}\n\n{user_content}"
    user_content += "\n\nThink step by step:"

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user_content},
    ]


# Test
messages = chain_of_thought(
    problem="Our API response time increased from 200ms to 2000ms after deploying v2.5. The deployment included a database migration, new caching layer, and updated authentication middleware. What should we investigate first?",
    context="We run on AWS ECS with RDS PostgreSQL and ElastiCache Redis."
)

print(f"CoT prompt:\n{messages[-1]['content']}\n")
response = call_llm(messages, max_tokens=500)
print(f"Analysis:\n{response[:400]}...")
