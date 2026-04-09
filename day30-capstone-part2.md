# Day 30: Capstone — DevOps Assistant Agent (Part 2)

## Today's Goal

Wire everything from Part 1 together into a functional DevOps Assistant Agent.

---

## Part 2: Agent Logic & Main Application

### Component 6: Agent Classes
```python
# agents.py
# - BaseAgent with tool calling and memory integration
# - DevOpsAdvisor — answers DevOps questions with documentation
# - IncidentResponder — diagnoses and plans incident response
# - CodeGenerator — generates Dockerfiles, K8s manifests, scripts
# - RouterAgent — classifies user intent and delegates
```

### Component 7: Main Application
```python
# main.py
# - Interactive CLI with command system
# - Startup: load config, initialize agents, load memory
# - Commands:
#   /help           — show commands
#   /stats          — usage statistics
#   /memory         — show stored memories
#   /export         — export conversation
#   /model [name]   — switch model
#   /clear          — clear conversation
#   /quit           — save and exit
# - Regular messages: route → process → respond
# - On exit: save memory, print stats
```

---

## Complete Agent Flow

```python
def handle_message(user_input: str):
    # 1. Input guardrails
    valid, errors = InputGuardrails.validate(user_input)
    if not valid:
        return f"Input rejected: {errors}"
    
    # 2. Budget check
    can_go, reason = budget.can_proceed()
    if not can_go:
        return f"Budget exceeded: {reason}"
    
    # 3. Log the request
    logger.log_event("user_message", {"content": user_input[:100]})
    
    # 4. Route to specialist
    routing = router.route(user_input)
    specialist = agents[routing["specialist"]]
    
    # 5. Build context (conversation + memory)
    context = memory.get_context()
    
    # 6. Get response
    response = specialist.respond(user_input, context=context)
    
    # 7. Output guardrails
    valid, errors = OutputGuardrails.validate(response)
    if not valid:
        logger.log_guardrail("output", True, str(errors))
        response = "I generated a response but it was flagged by safety checks."
    
    # 8. Update memory and stats
    memory.add("user", user_input)
    memory.add("assistant", response)
    budget.record_usage(tokens, cost)
    logger.log_llm_call(messages, response, tokens, cost)
    
    return response
```

---

## Evaluation Criteria

### Functionality (40 points)
- [ ] (10) Agent connects to at least one LLM provider (OpenAI, Anthropic, or Gemini) and gets real responses
- [ ] (10) Router correctly classifies queries to specialists
- [ ] (10) At least 4 tools work correctly
- [ ] (10) Conversation context maintained across messages

### Architecture (30 points)
- [ ] (10) Clean separation: config, tools, memory, guardrails, agents
- [ ] (10) Proper OOP with inheritance/composition
- [ ] (10) Error handling — no crashes on bad input

### Safety & Operations (30 points)
- [ ] (10) Input/output guardrails prevent issues
- [ ] (10) Budget controls track and limit spending
- [ ] (10) Structured logging captures all events

---

## Stretch Goals

If you finish early:
1. Add RAG with a local vector store of DevOps docs
2. Add async support for parallel tool execution
3. Add a "self-improvement" loop: agent evaluates its own answer
4. Web interface with Flask/FastAPI instead of CLI
5. Deploy to a Docker container (eat your own dog food!)

---

## Your Task

**Spend 90–120 minutes** building the full agent. Start with a minimal working version, then add features incrementally.

---

## Solutions

See [solutions/day29_capstone/](../solutions/day29_capstone/) for the complete implementation:
- [config.py](../solutions/day29_capstone/config.py)
- [tools.py](../solutions/day29_capstone/tools.py)
- [memory.py](../solutions/day29_capstone/memory.py)
- [guardrails.py](../solutions/day29_capstone/guardrails.py)
- [logger.py](../solutions/day29_capstone/logger.py)
- [agents.py](../solutions/day29_capstone/agents.py)
- [main.py](../solutions/day29_capstone/main.py)

---

## Course Complete! 🎉

### What You've Learned

| Week | Skills |
|------|--------|
| 1 | Python fundamentals: variables, strings, conditionals, loops, functions, data structures |
| 2 | Intermediate Python: files, error handling, modules, OOP, comprehensions, generators |
| 3 | AI integration: APIs, secrets, LLM APIs (OpenAI/Anthropic/Gemini), prompt engineering, data processing, async |
| 4 | AI Agents: architecture, tools, memory, LangChain, RAG, multi-agent, evaluation |

### What's Next?

1. **Build real projects** — Use your DevOps agent daily, keep improving it
2. **Learn LangGraph** — More advanced agent orchestration
3. **Explore CrewAI** — Multi-agent framework
4. **Study vector databases** — Pinecone, Weaviate, Qdrant
5. **Learn FastAPI** — Turn your agent into a web service
6. **Contribute to open source** — LangChain, AutoGen, etc.
7. **Get certified** — AWS/Azure AI certifications

### Key Resources
- [LangChain Docs](https://python.langchain.com/)
- [OpenAI Cookbook](https://cookbook.openai.com/)
- [Anthropic Docs](https://docs.anthropic.com/)
- [Google Gemini API Docs](https://ai.google.dev/gemini-api/docs)
- [Hugging Face](https://huggingface.co/)
- [Python Official Docs](https://docs.python.org/3/)
- [Real Python](https://realpython.com/)

**Keep building. The best way to learn is to ship.**
