# Day 21: Mini-Project — AI-Powered Q&A Bot

## Project Overview

Build a **real AI-powered Q&A bot** using everything from Week 3:
- REST API calls to OpenAI, Anthropic, or Gemini
- Secure API key management
- Prompt engineering
- Conversation history with token tracking
- Streaming responses
- Async capabilities

---

## Project Requirements

### Core Features
1. **Interactive CLI chat** with streaming responses
2. **System prompt selection** — choose bot personality at startup
3. **Conversation history** — maintains context across messages
4. **Token tracking** — shows usage and estimated cost per message
5. **Conversation export** — save to JSON or Markdown
6. **Multiple provider support** — switch between OpenAI, Anthropic, and Gemini
7. **Multiple model support** — switch models mid-conversation
7. **Structured commands**: `/model`, `/stats`, `/export`, `/clear`, `/quit`

### Stretch Goals
- Few-shot examples for specialized tasks
- Response caching (don't re-call for identical prompts)
- Markdown rendering in terminal
- Conversation loading from file

---

## Build Guide

### Step 1: Configuration
```python
# Load API keys from .env (OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY)
# Define available models per provider and their costs
# Define system prompt presets
```

### Step 2: Chat Engine Class
```python
# class ChatEngine:
#   - Supports OpenAI, Anthropic, and Gemini
#   - Manages the active provider's client
#   - Maintains message history
#   - Handles streaming and non-streaming calls
#   - Tracks token usage
```

### Step 3: Command Handler
```python
# Handle /commands:
# /provider [name] — switch provider (openai, anthropic, gemini)
# /model [name] — switch model
# /stats — show usage statistics  
# /export [path] — save conversation
# /clear — reset conversation
# /system [preset] — change system prompt
# /quit — exit with stats
```

### Step 4: Main Loop
```python
# Wire everything together
# Support both regular messages and commands
```

---

## Your Task

Spend 60–90 minutes building this. Use a real API key from any provider (OpenAI, Anthropic, or Gemini — Gemini has a free tier). Build it to support at least one provider with an easy path to add others.

---

## Evaluation Checklist

- [ ] Bot connects to at least one LLM provider (OpenAI, Anthropic, or Gemini)
- [ ] Provider can be switched via /provider command
- [ ] Streaming responses print token by token
- [ ] Conversation context is maintained
- [ ] Token usage is tracked per message and total
- [ ] Cost is estimated based on model
- [ ] Commands work: /provider, /model, /stats, /export, /clear, /quit
- [ ] Multiple system prompt presets available
- [ ] Error handling for API failures
- [ ] Clean code with proper classes and type hints
- [ ] Conversation can be exported to JSON

---

## Solutions

See [solutions/day21_qa_bot.py](../solutions/day21_qa_bot.py)

---

## Reflection

1. How does token tracking change how you use the bot?
2. What's the impact of temperature on response quality?
3. How would you add "memory" beyond the conversation window?
4. What would you need to deploy this for a team?

**Next week:** AI Agents — architecture, tools, memory, and frameworks →
