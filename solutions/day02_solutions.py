# ============================================
# Day 2 Solutions — Strings, Input & Output
# ============================================

# --- Exercise 1: String Inspector ---
text = "  The future of AI Agents is Autonomous Decision Making  "

# 1. Stripped
print(text.strip())

# 2. Upper case
print(text.upper())

# 3. Count 'A' case-insensitive
count_a = text.lower().count('a')
print(f"Letter 'a/A' appears {count_a} times")

# 4. Replace
print(text.replace("Autonomous", "Intelligent"))

# 5. Split into words
words = text.split()
print(words)

# 6. 5th word (0-indexed)
print(f"5th word: {words[5]}")

# 7. Reversed
print(text[::-1])


# --- Exercise 2: Interactive AI Model Card ---
print("\n--- Model Card Builder ---")
model_name = input("Enter model name: ") if __name__ == "__main__" else "GPT-4"
version = input("Enter version: ") if __name__ == "__main__" else "4.0"
params = input("Enter parameter count: ") if __name__ == "__main__" else "1760000000"
use_case = input("Enter top use case: ") if __name__ == "__main__" else "Code Generation"

# Format parameter count with commas
params_formatted = f"{int(params):,}"

width = 34
print(f"╔{'═' * width}╗")
print(f"║{'AI MODEL CARD':^{width}}║")
print(f"╠{'═' * width}╣")
print(f"║ {'Name:':<12} {model_name:<{width - 14}}║")
print(f"║ {'Version:':<12} {version:<{width - 14}}║")
print(f"║ {'Parameters:':<12} {params_formatted:<{width - 14}}║")
print(f"║ {'Use Case:':<12} {use_case:<{width - 14}}║")
print(f"╚{'═' * width}╝")


# --- Exercise 3: Prompt Builder ---
def build_prompt(role: str, topic: str, difficulty: str) -> str:
    difficulty_instructions = {
        "beginner": "Use simple examples and avoid jargon. Explain concepts step by step.",
        "intermediate": "Use practical examples. You can assume basic knowledge.",
        "advanced": "Use advanced examples, edge cases, and best practices. Be thorough."
    }
    
    instruction = difficulty_instructions.get(
        difficulty.lower(),
        "Adjust your explanation to the user's level."
    )
    
    return f"You are a {role}. Explain {topic} at a {difficulty} level. {instruction}"


# Test
print("\n--- Prompt Builder ---")
prompt = build_prompt("Python tutor", "list comprehensions", "beginner")
print(prompt)

prompt = build_prompt("DevOps mentor", "Kubernetes networking", "advanced")
print(prompt)
