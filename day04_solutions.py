# ============================================
# Day 4 Solutions — Loops & Iteration
# ============================================

import random

# --- Exercise 1: Token Counter ---
messages = [
    "Hello, how are you today?",
    "I need help deploying a Kubernetes cluster on AWS",
    "Can you write a Python script to parse JSON logs?",
    "What is the difference between Docker and Podman?",
    "Explain CI/CD pipelines in simple terms"
]

print("--- Token Counter ---")
total_tokens = 0
for i, msg in enumerate(messages, 1):
    word_count = len(msg.split())
    total_tokens += word_count
    print(f"  Message {i}: {word_count:>2} tokens | \"{msg}\"")

average = total_tokens / len(messages)
print(f"\nTotal tokens: {total_tokens}")
print(f"Average tokens per message: {average:.1f}")


# --- Exercise 2: Retry Simulator ---
print("\n--- Retry Simulator ---")
success_rates = [0.2, 0.4, 0.6, 0.8, 0.95]
connected = False

for attempt in range(5):
    chance = success_rates[attempt]
    backoff = 2 ** attempt
    roll = random.random()
    success = roll < chance

    if success:
        print(f"  Attempt {attempt + 1}: SUCCESS ✅ (chance: {chance*100:.0f}%)")
        print(f"  Connected on attempt {attempt + 1}!")
        connected = True
        break
    else:
        print(f"  Attempt {attempt + 1}: FAILED ❌ (chance: {chance*100:.0f}%, backoff: {backoff}s)")

if not connected:
    print("  Service unavailable after 5 attempts.")


# --- Exercise 3: Number Guessing Game ---
def guessing_game():
    number = random.randint(1, 100)
    max_guesses = 7

    print("\n--- Number Guessing Game ---")
    print("I'm thinking of a number between 1 and 100.")
    print(f"You have {max_guesses} guesses.\n")

    for attempt in range(1, max_guesses + 1):
        try:
            guess = int(input(f"Guess {attempt}/{max_guesses}: "))
        except ValueError:
            print("Please enter a valid number!")
            continue

        if guess == number:
            print(f"🎉 You got it in {attempt} tries! The number was {number}.")
            return
        elif guess < number:
            print("Too low! ⬆️")
        else:
            print("Too high! ⬇️")

    print(f"💀 Out of guesses! The number was {number}.")


# Uncomment to play:
# guessing_game()

# Non-interactive demo
print("\n--- Guessing Game Demo (automated) ---")
number = random.randint(1, 100)
low, high = 1, 100

for attempt in range(1, 8):
    guess = (low + high) // 2  # Binary search strategy
    if guess == number:
        print(f"  Guess {attempt}: {guess} → Correct! 🎉")
        break
    elif guess < number:
        print(f"  Guess {attempt}: {guess} → Too low")
        low = guess + 1
    else:
        print(f"  Guess {attempt}: {guess} → Too high")
        high = guess - 1
else:
    print(f"  Failed. Number was {number}")
