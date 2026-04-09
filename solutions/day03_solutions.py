# ============================================
# Day 3 Solutions — Conditionals & Boolean Logic
# ============================================

# --- Exercise 1: Token Budget Checker ---
def check_budget(total_budget: int, tokens_used: int):
    remaining = total_budget - tokens_used
    pct_remaining = (remaining / total_budget) * 100 if total_budget > 0 else 0

    if remaining <= 0:
        status = "Budget exhausted! ❌"
    elif pct_remaining < 25:
        status = "Budget critical 🚨"
    elif pct_remaining < 75:
        status = "Budget moderate ⚠️"
    else:
        status = "Budget healthy ✅"

    print(f"Total: {total_budget}, Used: {tokens_used}, Remaining: {remaining}")
    print(f"Percentage remaining: {pct_remaining:.1f}%")
    print(f"Status: {status}")

print("--- Budget Checker ---")
check_budget(10000, 2000)
print()
check_budget(10000, 8000)
print()
check_budget(10000, 10500)


# --- Exercise 2: API Key Validator ---
def validate_api_key(key: str) -> str:
    if not key.startswith("sk-"):
        return "Invalid: Key must start with 'sk-'"
    if len(key) < 20:
        return f"Invalid: Key must be at least 20 characters (got {len(key)})"
    if " " in key:
        return "Invalid: Key must not contain spaces"
    if not any(c.isdigit() for c in key):
        return "Invalid: Key must contain at least one digit"
    return "Valid"

print("\n--- API Key Validator ---")
test_keys = [
    "sk-abc123def456ghi789jkl",
    "pk-abc123",
    "sk-short",
    "sk-abcdefghijklmnopqrs",
    "sk-abcdefghijklm nopqr1",
    "sk-abcdefghijklmnopqrs1",
]
for key in test_keys:
    result = validate_api_key(key)
    print(f"  '{key}' → {result}")


# --- Exercise 3: Agent Action Classifier ---
def classify_action(message: str) -> str:
    msg_lower = message.lower()

    if "weather" in msg_lower or "temperature" in msg_lower:
        return "weather_tool"

    if "calculate" in msg_lower or "math" in msg_lower or any(c.isdigit() for c in message):
        return "calculator_tool"

    if "search" in msg_lower or "find" in msg_lower or "look up" in msg_lower:
        return "search_tool"

    if "remember" in msg_lower or "save" in msg_lower or "note" in msg_lower:
        return "memory_tool"

    return "general_chat"

print("\n--- Action Classifier ---")
test_messages = [
    "What's the weather like today?",
    "Calculate 15% of 200",
    "Search for Python tutorials",
    "Remember that my server is on port 8080",
    "Hello, how are you?",
    "Find me the best Docker practices",
    "What's the temperature in London?",
    "Save this note: deploy on Friday",
]
for msg in test_messages:
    action = classify_action(msg)
    print(f"  '{msg}' → {action}")
