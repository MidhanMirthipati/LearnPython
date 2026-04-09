# Day 14: Mini-Project — Conversation Logger with OOP

## Project Overview

Build a **full-featured conversation logging system** using everything from Week 2:
- File I/O and JSON persistence
- Error handling and validation
- Modules and imports
- OOP with inheritance and composition
- Comprehensions and generators

---

## Project Requirements

### Core Classes @
1. **`Message`** — A single message with role, content, timestamp, token estimate
2. **`Conversation`** — A list of Messages with add/search/export methods
3. **`ConversationStore`** — Manages multiple conversations, saves/loads from disk
4. **`AgentSimulator`** — Simulates an AI agent (keyword-based responses)
5. **`Logger`** — Logs all interactions to a file

### Features
- Create, continue, and switch between conversations
- Save/load conversations to/from JSON files
- Search across all conversations for a keyword
- Display usage statistics (tokens, message counts)
- Export a conversation to readable Markdown

### Commands
```
/new [title]       — Start a new conversation
/list              — List all conversations
/switch [id]       — Switch to a different conversation
/history           — Show current conversation
/search [keyword]  — Search across all conversations
/stats             — Show usage statistics
/export            — Export current conversation to Markdown
/save              — Save all conversations
/quit              — Save and exit
```

---

## Build Guide

### Step 1: Message Class
```python
# Attributes: role, content, timestamp, token_estimate
# Methods: to_dict(), from_dict() (class method), __str__
```

### Step 2: Conversation Class
```python
# Attributes: id, title, messages list, created_at
# Methods: add_message(), get_messages(), search(), 
#          token_count(), to_dict(), from_dict(), export_markdown()
```

### Step 3: ConversationStore
```python
# Attributes: conversations dict, storage_path
# Methods: create(), get(), list_all(), save_to_disk(), load_from_disk()
```

### Step 4: AgentSimulator
```python
# A simple keyword-based responder similar to Day 7
# But built with OOP and using the Message/Conversation classes
```

### Step 5: Main Application Loop
```python
# Wire everything together in a main() function with the command system
```

---

## Your Task

Spend 60–90 minutes building this from scratch. Then compare with the solution.

---

## Evaluation Checklist

- [ ] Messages store role, content, timestamp, token estimate
- [ ] Conversations can be created, searched, and exported
- [ ] ConversationStore persists conversations to JSON files
- [ ] Multiple conversations can be managed simultaneously
- [ ] Commands work correctly
- [ ] Error handling prevents crashes on bad input
- [ ] Code is organized with proper classes and methods
- [ ] Uses list comprehensions where appropriate
- [ ] All methods have type hints

---

## Solutions

See [solutions/day14_conversation_logger.py](../solutions/day14_conversation_logger.py)

---

## Reflection

1. How does OOP make this easier compared to pure functions + dicts?
2. Where did composition vs inheritance make sense?
3. What would break if two users used this simultaneously?
4. How would you add real AI responses (API calls) to this?

**Next week:** HTTP APIs, OpenAI, Prompt Engineering, and building AI-powered bots →
