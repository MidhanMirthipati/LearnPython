# ============================================
# Day 6 Solutions — Lists, Tuples & Dictionaries
# ============================================

# --- Exercise 1: Model Leaderboard ---
models = [
    {"name": "GPT-4o", "score": 92.5, "cost": 0.005, "provider": "OpenAI"},
    {"name": "Claude Sonnet", "score": 91.8, "cost": 0.003, "provider": "Anthropic"},
    {"name": "Gemini 2.5 Pro", "score": 90.3, "cost": 0.00125, "provider": "Google"},
    {"name": "GPT-4o-mini", "score": 85.2, "cost": 0.00015, "provider": "OpenAI"},
    {"name": "Gemini Flash", "score": 88.7, "cost": 0.0001, "provider": "Google"},
]

# 1. Sort by score and print ranked table
print("--- Model Leaderboard ---")
sorted_by_score = sorted(models, key=lambda m: m["score"], reverse=True)
print(f"{'Rank':<6} {'Model':<12} {'Score':<8} {'Cost':<10} {'Provider'}")
print("-" * 50)
for rank, model in enumerate(sorted_by_score, 1):
    print(f"{rank:<6} {model['name']:<12} {model['score']:<8} ${model['cost']:<9} {model['provider']}")

# 2. All models from OpenAI
openai_models = [m["name"] for m in models if m["provider"] == "OpenAI"]
print(f"\nOpenAI models: {openai_models}")

# 3. Cheapest model
cheapest = min(models, key=lambda m: m["cost"])
print(f"Cheapest: {cheapest['name']} (${cheapest['cost']})")

# 4. Models with score > 90
top_models = [m["name"] for m in models if m["score"] > 90]
print(f"Score > 90: {top_models}")

# 5. Average score
avg_score = sum(m["score"] for m in models) / len(models)
print(f"Average score: {avg_score:.1f}")

# 6. Provider → model names mapping
provider_models = {}
for m in models:
    provider = m["provider"]
    if provider not in provider_models:
        provider_models[provider] = []
    provider_models[provider].append(m["name"])
print(f"Provider mapping: {provider_models}")


# --- Exercise 2: Inventory Tracker ---
print("\n--- Inventory Tracker ---")

inventory = {}

def add_item(item: str, quantity: int):
    if item in inventory:
        inventory[item] += quantity
    else:
        inventory[item] = quantity
    print(f"  Added {quantity} x {item}. Total: {inventory[item]}")

def remove_item(item: str, quantity: int):
    if item not in inventory:
        print(f"  Item '{item}' not found in inventory.")
        return
    inventory[item] = max(0, inventory[item] - quantity)
    print(f"  Removed {quantity} x {item}. Remaining: {inventory[item]}")

def check_item(item: str):
    qty = inventory.get(item, 0)
    print(f"  {item}: {qty} in stock")

def list_all():
    if not inventory:
        print("  Inventory is empty.")
        return
    print("  Current inventory:")
    for item, qty in sorted(inventory.items()):
        print(f"    {item}: {qty}")

def low_stock(threshold: int = 5):
    low = {k: v for k, v in inventory.items() if v < threshold}
    if low:
        print(f"  Low stock (< {threshold}):")
        for item, qty in low.items():
            print(f"    ⚠️ {item}: {qty}")
    else:
        print("  All items sufficiently stocked.")

# Test
add_item("docker-image", 10)
add_item("k8s-node", 3)
add_item("ssl-cert", 2)
add_item("docker-image", 5)
remove_item("k8s-node", 1)
list_all()
low_stock(5)


# --- Exercise 3: Message Deduplicator ---
print("\n--- Message Deduplicator ---")

messages = [
    {"id": 1, "text": "Hello", "timestamp": "10:00"},
    {"id": 2, "text": "How are you?", "timestamp": "10:01"},
    {"id": 1, "text": "Hello", "timestamp": "10:02"},
    {"id": 3, "text": "Help me", "timestamp": "10:03"},
    {"id": 2, "text": "How are you?", "timestamp": "10:04"},
]

seen_ids = set()
deduplicated = []
for msg in messages:
    if msg["id"] not in seen_ids:
        seen_ids.add(msg["id"])
        deduplicated.append(msg)

print(f"Original: {len(messages)} messages")
print(f"Deduplicated: {len(deduplicated)} messages")
for msg in deduplicated:
    print(f"  id={msg['id']}, text='{msg['text']}', time={msg['timestamp']}")
