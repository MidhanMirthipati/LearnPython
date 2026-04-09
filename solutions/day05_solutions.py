# ============================================
# Day 5 Solutions — Functions & Scope
# ============================================

# --- Exercise 1: Token Estimator Suite ---
def estimate_tokens(text: str) -> int:
    """Estimate token count (~4 chars per token)."""
    return max(1, len(text) // 4)


def calculate_cost(tokens: int, model: str) -> float:
    """Calculate cost based on model pricing per 1K tokens."""
    rates = {
        "gpt-4o-mini": 0.00015,
        "gpt-3.5": 0.002,
        "claude": 0.015,
    }
    rate = rates.get(model, 0.002)
    return (tokens / 1000) * rate


def format_cost(cost: float) -> str:
    """Format cost as a dollar string."""
    return f"${cost:.4f}"


def analyze_prompt(text: str, model: str = "gpt-3.5") -> dict:
    """Full analysis: tokens, cost, and more."""
    tokens = estimate_tokens(text)
    cost = calculate_cost(tokens, model)
    return {
        "text_length": len(text),
        "estimated_tokens": tokens,
        "model": model,
        "cost": format_cost(cost),
    }


print("--- Token Estimator Suite ---")
prompts = [
    "Hello",
    "Explain how Docker containers work in production environments",
    "Write a comprehensive guide to Kubernetes networking including Services, Ingress, NetworkPolicies, and CNI plugins with examples for each",
]

for prompt in prompts:
    result = analyze_prompt(prompt, model="gpt-4o-mini")
    print(f"  \"{prompt[:50]}...\"")
    for k, v in result.items():
        print(f"    {k}: {v}")
    print()


# --- Exercise 2: Prompt Template Engine ---
_templates = {}


def create_template(name: str, template_string: str):
    """Store a prompt template."""
    _templates[name] = template_string
    print(f"  Template '{name}' created.")


def list_templates():
    """Print all template names."""
    print("  Available templates:")
    for name in _templates:
        print(f"    - {name}")


def render_template(name: str, **variables) -> str:
    """Fill in template placeholders."""
    if name not in _templates:
        return f"Error: Template '{name}' not found"

    result = _templates[name]
    for key, value in variables.items():
        result = result.replace(f"{{{key}}}", str(value))
    return result


print("--- Prompt Template Engine ---")
create_template("qa", "Context: {context}\nQuestion: {question}\nAnswer:")
create_template("role", "You are a {role}. Help with {task}. Be {style}.")
create_template("review", "Review this {language} code:\n```\n{code}\n```")

list_templates()

result = render_template("qa",
    context="Python is a programming language created by Guido van Rossum.",
    question="Who created Python?"
)
print(f"\nRendered:\n{result}")

result = render_template("role",
    role="DevOps engineer",
    task="Docker troubleshooting",
    style="concise"
)
print(f"\nRendered:\n{result}")


# --- Exercise 3: Function Dispatcher ---
def greet():
    print("  Hello! Welcome to the DevOps Bot.")

def farewell():
    print("  Goodbye! Have a great day.")

def help_menu():
    print("  Available commands: greet, farewell, help, version, status, quit")

def version():
    print("  DevOps Bot v1.0.0")

def status():
    print("  All systems operational. ✅")

commands = {
    "greet": greet,
    "farewell": farewell,
    "help": help_menu,
    "version": version,
    "status": status,
}

print("\n--- Function Dispatcher Demo ---")
test_commands = ["help", "version", "status", "greet", "unknown", "farewell"]
for cmd in test_commands:
    print(f"\n> {cmd}")
    if cmd in commands:
        commands[cmd]()
    else:
        print(f"  Unknown command: '{cmd}'. Type 'help' for available commands.")
