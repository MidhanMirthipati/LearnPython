# Day 7: Mini-Project — CLI Chatbot Skeleton

## Project Overview

Build a **command-line chatbot** that ties together everything from Week 1:
- Variables & data types
- String manipulation & f-strings
- Conditionals & boolean logic
- Loops & iteration
- Functions
- Lists & dictionaries

This chatbot won't use real AI yet — it will use pattern matching and templates. In Week 3, you'll upgrade it to call a real LLM.

---

## Project Requirements

### Core Features
1. **Greeting**: Ask for the user's name, greet them personally
2. **Command system**: Respond to commands like `/help`, `/tools`, `/history`, `/quit`
3. **Simple responses**: Match keywords in user messages to canned responses
4. **Conversation history**: Store all messages in a list of dicts
5. **Token counting**: Track approximate token usage
6. **Session summary**: On `/quit`, display session stats

### Stretch Goals
- Add a `/search <query>` command that pretends to search
- Add a `/config` command to change the bot's "personality"
- Add response templates with random variation

---

## Step-by-Step Build Guide

### Step 1: Setup and Configuration
```python
# Define your bot's configuration as a dictionary
BOT_CONFIG = {
    "name": "PyBot",
    "version": "1.0",
    "personality": "helpful",
    "max_history": 100,
}
```

### Step 2: Response Knowledge Base
```python
# Create a knowledge base of keyword → response mappings
RESPONSES = {
    "hello": "Hello! How can I help you today?",
    "help": "I can answer questions about Python, DevOps, and AI!",
    "python": "Python is a versatile programming language...",
    # ... add more
}
```

### Step 3: Core Functions
```python
# Build these functions:
# - find_response(user_message) → str
# - estimate_tokens(text) → int
# - add_to_history(role, content, history) → None
# - display_history(history) → None
# - get_session_stats(history) → dict
```

### Step 4: Main Loop
```python
# Build the chat loop:
# 1. Greet user
# 2. Loop: get input → process → respond
# 3. Handle commands (starting with /)
# 4. Handle regular messages (keyword matching)
# 5. On quit: show stats
```

---

## Your Task

**Build the chatbot from scratch.** Use the guide above as a skeleton, but write all the code yourself. Spend 45–60 minutes on this.

When done, compare your solution with [solutions/day07_chatbot.py](../solutions/day07_chatbot.py)

---

## Evaluation Checklist

- [ ] Bot greets the user by name
- [ ] `/help` displays available commands
- [ ] `/history` shows conversation history
- [ ] `/quit` shows session statistics and exits
- [ ] Regular messages get keyword-matched responses
- [ ] Unknown inputs get a graceful "I don't understand" response
- [ ] Token usage is tracked
- [ ] Code uses functions (not all in one giant block)
- [ ] Code is clean, readable, with meaningful variable names

---

## Solutions

See [solutions/day07_chatbot.py](../solutions/day07_chatbot.py) for the complete solution.

---

## Reflection Questions

1. What was the hardest part of building this?
2. What would you need to make this chatbot actually useful?
3. How would you add "memory" — making the bot remember facts from earlier?
4. What would change if you connected this to a real AI model?

**Next week:** File I/O, error handling, OOP, and more advanced Python →
