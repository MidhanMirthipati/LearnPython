# Day 29: Capstone — DevOps Assistant Agent (Part 1)

## Project Overview

Build a complete **DevOps Assistant Agent** that combines everything you've learned. This is a real, functional tool you can use in your daily work.

---

## Architecture

```
                          ┌─────────────┐
                          │    User     │
                          └──────┬──────┘
                                 │
                          ┌──────▼──────┐
                          │   Router    │
                          │   Agent     │
                          └──────┬──────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
       ┌──────▼──────┐   ┌──────▼──────┐   ┌──────▼──────┐
       │   DevOps    │   │  Incident   │   │    Code     │
       │  Advisor    │   │  Responder  │   │  Generator  │
       └──────┬──────┘   └──────┬──────┘   └──────┬──────┘
              │                  │                  │
       ┌──────▼──────────────────▼──────────────────▼──────┐
       │                  Tool Belt                          │
       │  [search] [health_check] [log_search] [dockerfile] │
       │  [k8s_helper] [cost_calculator] [memory]           │
       └────────────────────┬───────────────────────────────┘
                            │
       ┌────────────────────▼───────────────────────────────┐
       │              Support Systems                        │
       │  [Logger] [Guardrails] [Budget] [Memory Store]     │
       └────────────────────────────────────────────────────┘
```

---

## Part 1: Core Infrastructure (Today)

Build these components:

### Component 1: Configuration
```python
# config.py
# - Load from .env
# - Model settings, tool settings
# - Budget limits
# - Logging configuration
```

### Component 2: Tool Registry
```python
# tools.py
# Build at least 6 tools:
# 1. search_docs(query) — search DevOps documentation
# 2. check_service(service_name) — health check
# 3. search_logs(service, pattern) — log analysis
# 4. generate_dockerfile(language, app_type) — Dockerfile generator
# 5. generate_k8s_manifest(app_name, image, replicas) — K8s YAML
# 6. estimate_cost(tokens, model) — cost calculator
```

### Component 3: Memory System
```python
# memory.py
# - ConversationMemory with windowing
# - LongTermMemory with persistence
# - Scratchpad for multi-step tasks
```

### Component 4: Guardrails
```python
# guardrails.py
# - Input validation
# - Output validation
# - Budget controller
```

### Component 5: Logger
```python
# logger.py
# - Structured event logging
# - File and console output
# - Event export
```

---

## File Structure to Create

```
devops_agent/
├── .env                  # API keys (DO NOT commit)
├── .env.example          # Template
├── .gitignore
├── requirements.txt
├── config.py             # Configuration loader
├── tools.py              # Tool definitions and implementations
├── memory.py             # Memory components
├── guardrails.py         # Input/output guardrails
├── logger.py             # Structured logging
├── agents.py             # Agent classes (Part 2)
├── main.py               # Entry point (Part 2)
└── data/
    └── devops_docs.json  # Knowledge base
```

---

## Today's Task

Build Components 1–5 as separate Python modules. Test each module independently. Tomorrow you'll wire them into the full agent.

**Spend 90 minutes on this.** Focus on clean code with proper error handling.

---

## Solutions

See [solutions/day29_capstone/](../solutions/day29_capstone/) for all component files.
