# ============================================
# Day 1 Solutions — Setup, Variables & Data Types
# ============================================

# --- Exercise 1: Variable Practice ---
model_name = "gpt-4o-mini"
parameters = 1760000000000
context_window = 128000
is_multimodal = True
cost_per_token = 0.00003

print(f"""
AI Model Summary
================
Model:          {model_name}
Parameters:     {parameters:,}
Context Window: {context_window:,} tokens
Multimodal:     {is_multimodal}
Cost:           ${cost_per_token} per token
""")


# --- Exercise 2: Token Cost Calculator ---
input_tokens = 5000
output_tokens = 2000
input_cost_per_token = 0.00003
output_cost_per_token = 0.00006

input_cost = input_tokens * input_cost_per_token
output_cost = output_tokens * output_cost_per_token
total_cost = input_cost + output_cost

print(f"Input cost:  ${input_cost:.2f}")
print(f"Output cost: ${output_cost:.2f}")
print(f"Total cost:  ${total_cost:.2f}")


# --- Exercise 3: Type Detective ---
print("\nType Detective:")
print(f"a) 42       → {type(42)}")         # int
print(f"b) 42.0     → {type(42.0)}")       # float
print(f"c) '42'     → {type('42')}")       # str
print(f"d) True     → {type(True)}")       # bool
print(f"e) 3 + 4.0  → {type(3 + 4.0)}")   # float (int + float = float)
print(f"f) 10 / 2   → {type(10 / 2)}")     # float (division always returns float)
print(f"g) 10 // 2  → {type(10 // 2)}")    # int (floor division)
