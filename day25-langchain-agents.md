# Day 25: Building Agents with LangChain

## Learning Goals
- Understand the LangChain framework
- Build agents with LangChain's agent executor
- Use built-in and custom tools
- Chain LLM calls together

---

## 1. What is LangChain?

LangChain is a framework that simplifies building LLM-powered applications:
- **Chat models**: Unified interface for OpenAI, Anthropic, Google Gemini, and more
- **Prompt templates**: Reusable prompt builders
- **Chains**: Sequence of LLM calls
- **Agents**: LLM + tools with reasoning loops
- **Memory**: Conversation and long-term storage
- **Retrieval**: Connect LLMs to your data

```bash
pip install langchain langchain-openai langchain-anthropic langchain-google-genai langchain-community
```

---

## 2. Basic LangChain Usage — All Three Providers

LangChain's power is a **unified interface** — swap providers with one line.

### OpenAI
```python
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

response = llm.invoke([
    SystemMessage(content="You are a DevOps expert."),
    HumanMessage(content="What is Infrastructure as Code?")
])
print(response.content)
```

### Anthropic (Claude)
```python
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv

load_dotenv()

llm = ChatAnthropic(model="claude-sonnet-4-20250514", temperature=0.7)

response = llm.invoke([
    SystemMessage(content="You are a DevOps expert."),
    HumanMessage(content="What is Infrastructure as Code?")
])
print(response.content)
```

### Google Gemini
```python
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7)

response = llm.invoke([
    SystemMessage(content="You are a DevOps expert."),
    HumanMessage(content="What is Infrastructure as Code?")
])
print(response.content)
```

> **Key insight:** Notice how the rest of the code is identical — only the `llm = ...` line changes. This is LangChain's biggest advantage: write your agent once, swap providers freely.

---

## 3. Prompt Templates

```python
from langchain_core.prompts import ChatPromptTemplate

# Define a template
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a {role} specialist. Respond in {style} style."),
    ("human", "{question}")
])

# Create a chain: prompt → LLM
chain = prompt | llm

# Invoke with variables
response = chain.invoke({
    "role": "Kubernetes",
    "style": "concise, bullet-point",
    "question": "What are the key components of a K8s cluster?"
})
print(response.content)
```

---

## 4. Building Tools

```python
from langchain_core.tools import tool
import json

@tool
def search_documentation(query: str) -> str:
    """Search the DevOps documentation for a topic."""
    docs = {
        "docker": "Docker is a container platform. Key commands: build, run, push.",
        "kubernetes": "K8s orchestrates containers. Key objects: Pod, Service, Deployment.",
        "terraform": "Terraform is IaC. Commands: init, plan, apply, destroy.",
        "ansible": "Ansible is config management. Uses YAML playbooks.",
    }
    for key, value in docs.items():
        if key in query.lower():
            return value
    return f"No documentation found for: {query}"

@tool
def run_health_check(service_name: str) -> str:
    """Check the health status of a service."""
    import random
    statuses = ["healthy", "healthy", "healthy", "degraded", "down"]
    status = random.choice(statuses)
    return json.dumps({
        "service": service_name,
        "status": status,
        "response_time_ms": random.randint(10, 500),
        "last_checked": "2024-01-15T10:30:00Z"
    })

@tool
def calculate_cost(tokens: int, model: str = "gpt-3.5-turbo") -> str:
    """Calculate the cost of an API call given tokens and model."""
    rates = {
        "gpt-4o": 0.005,
        "gpt-4o-mini": 0.00015,
        "claude-sonnet-4-20250514": 0.003,
        "claude-haiku-4-20250514": 0.0008,
        "gemini-2.0-flash": 0.0001,
        "gemini-2.5-pro": 0.00125,
    }
    rate = rates.get(model, 0.002)
    cost = (tokens / 1000) * rate
    return f"Cost for {tokens} tokens on {model}: ${cost:.4f}"

# List our tools
tools = [search_documentation, run_health_check, calculate_cost]
```

---

## 5. Creating an Agent

```python
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv

load_dotenv()

# Setup — pick any provider (all work the same with LangChain)
# Option A: OpenAI
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Option B: Anthropic
# from langchain_anthropic import ChatAnthropic
# llm = ChatAnthropic(model="claude-sonnet-4-20250514", temperature=0)

# Option C: Google Gemini
# from langchain_google_genai import ChatGoogleGenerativeAI
# llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)

# Agent prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a DevOps assistant agent. You have access to tools for:
- Searching documentation
- Checking service health
- Calculating API costs

Use your tools when needed. Be helpful and concise."""),
    MessagesPlaceholder("chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder("agent_scratchpad"),
])

# Create the agent
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Run it!
result = agent_executor.invoke({
    "input": "Check the health of the auth-service and then find documentation about Docker"
})
print(f"\nFinal: {result['output']}")
```

---

## 6. Agent with Memory

```python
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# Create message history store
message_histories = {}

def get_session_history(session_id: str):
    if session_id not in message_histories:
        message_histories[session_id] = InMemoryChatMessageHistory()
    return message_histories[session_id]

# Wrap agent with memory
agent_with_memory = RunnableWithMessageHistory(
    agent_executor,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
)

# Multi-turn conversation
config = {"configurable": {"session_id": "user-001"}}

response1 = agent_with_memory.invoke(
    {"input": "What is Kubernetes?"},
    config=config
)
print(response1["output"])

response2 = agent_with_memory.invoke(
    {"input": "How does it compare to Docker Swarm?"},  # Uses context!
    config=config
)
print(response2["output"])
```

---

## 7. Chains: Composing Multiple Steps

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser

# Pick any provider — chains work identically with all of them
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
# Or: from langchain_anthropic import ChatAnthropic
#     llm = ChatAnthropic(model="claude-sonnet-4-20250514", temperature=0)
# Or: from langchain_google_genai import ChatGoogleGenerativeAI
#     llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)

# Chain 1: Analyze → Plan → Implement
analyze_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a DevOps architect. Analyze the requirement and identify key challenges."),
    ("human", "{requirement}")
])

plan_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a project planner. Create a step-by-step plan based on this analysis."),
    ("human", "Analysis: {analysis}\n\nCreate an implementation plan.")
])

implement_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a DevOps engineer. Write implementation code/config based on this plan."),
    ("human", "Plan: {plan}\n\nProvide the implementation.")
])

# Build chains
analyze_chain = analyze_prompt | llm | StrOutputParser()
plan_chain = plan_prompt | llm | StrOutputParser()
implement_chain = implement_prompt | llm | StrOutputParser()

# Sequential execution
def full_pipeline(requirement: str) -> dict:
    analysis = analyze_chain.invoke({"requirement": requirement})
    print(f"📋 Analysis complete ({len(analysis)} chars)")
    
    plan = plan_chain.invoke({"analysis": analysis})
    print(f"📝 Plan complete ({len(plan)} chars)")
    
    implementation = implement_chain.invoke({"plan": plan})
    print(f"🔧 Implementation complete ({len(implementation)} chars)")
    
    return {
        "requirement": requirement,
        "analysis": analysis,
        "plan": plan,
        "implementation": implementation
    }

# Run the pipeline
result = full_pipeline("Set up a CI/CD pipeline for a Python microservice that deploys to Kubernetes")
```

---

## 8. Exercises

### Exercise 1: Custom Agent with 5 Tools
```python
# Build a LangChain agent with these tools:
# 1. file_reader — reads a file (simulated)
# 2. web_search — searches the web (simulated)
# 3. code_executor — runs Python code (safely simulated)
# 4. note_taker — saves notes
# 5. note_reader — retrieves saved notes
# Test with a multi-step query that uses at least 3 tools
```

### Exercise 2: Multi-Chain Pipeline
```python
# Build a pipeline that: 
# 1. Takes a user's question
# 2. Classifies it (devops, coding, general)
# 3. Routes to the appropriate chain/prompt
# 4. Formats the output based on classification
# Each classifier/handler is a separate chain
```

### Exercise 3: Agent Comparison
```python
# Build the SAME agent two ways:
# 1. Using the SimpleAgent from Day 22 (manual)
# 2. Using LangChain
# Compare: lines of code, readability, features, ease of extension
# Document your findings
```

---

## Solutions

See [solutions/day25_solutions.py](../solutions/day25_solutions.py)

---

## Key Takeaways
- LangChain provides a **provider-agnostic** framework — swap between OpenAI, Anthropic, and Gemini with one line
- Install provider packages: `langchain-openai`, `langchain-anthropic`, `langchain-google-genai`
- `@tool` decorator makes creating tools simple
- `AgentExecutor` handles the agent loop automatically
- Chains compose LLM calls sequentially: `prompt | llm | parser`
- Memory integration keeps conversation context
- LangChain vs manual: trade-off between convenience and control

**Tomorrow:** RAG — Retrieval Augmented Generation →
