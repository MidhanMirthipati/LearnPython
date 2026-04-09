# Day 22: What Are AI Agents — Architecture & Concepts

## Learning Goals
- Understand what makes an AI agent different from a chatbot
- Learn the core agent loop: Perceive → Think → Act
- Understand agent architectures (ReAct, Plan-and-Execute)
- Build a minimal agent from scratch (no frameworks)

---

## 1. Chatbot vs Agent

| Feature | Chatbot | Agent |
|---------|---------|-------|
| Responds to user | ✅ | ✅ |
| Maintains conversation | ✅ | ✅ |
| Uses tools | ❌ | ✅ |
| Takes autonomous actions | ❌ | ✅ |
| Makes multi-step plans | ❌ | ✅ |
| Loops until task is done | ❌ | ✅ |

**Agent = LLM + Tools + Loop**

---

## 2. The Agent Loop

```
┌──────────────────────────────────────┐
│           USER REQUEST               │
└──────────────┬───────────────────────┘
               ▼
┌──────────────────────────────────────┐
│  1. PERCEIVE: Read input + context   │
│     (user message, tool results,     │
│      memory, conversation history)   │
└──────────────┬───────────────────────┘
               ▼
┌──────────────────────────────────────┐
│  2. THINK: LLM decides what to do   │
│     - Answer directly?              │
│     - Use a tool?                    │
│     - Ask for clarification?         │
└──────────────┬───────────────────────┘
               ▼
┌──────────────────────────────────────┐
│  3. ACT: Execute the decision        │
│     - Call a tool / API              │
│     - Return answer to user          │
│     - Store in memory                │
└──────────────┬───────────────────────┘
               ▼
         Is task complete?
          ├── No → Loop back to PERCEIVE
          └── Yes → Return final answer
```

---

## 3. ReAct Pattern (Reason + Act)

The most common agent pattern:

```
Thought: I need to find the current weather in London
Action: search("current weather London")
Observation: London is currently 15°C, partly cloudy
Thought: I have the information the user needs
Action: respond("The weather in London is currently 15°C and partly cloudy.")
```

---

## 4. Building a Minimal Agent from Scratch

```python
import json
from openai import OpenAI  # Using OpenAI here; see Day 17 for Anthropic/Gemini equivalents
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

# --- Tool Definitions ---
def search_web(query: str) -> str:
    """Simulate a web search."""
    fake_results = {
        "python version": "The latest Python version is 3.12 (released Oct 2024).",
        "kubernetes": "Kubernetes 1.29 was released in December 2024.",
        "docker": "Docker 25.0 is the latest stable release.",
    }
    for key, result in fake_results.items():
        if key in query.lower():
            return result
    return f"No results found for: {query}"

def calculate(expression: str) -> str:
    """Safely evaluate a math expression."""
    try:
        allowed_names = {"__builtins__": {}}
        result = eval(expression, allowed_names)
        return str(result)
    except Exception as e:
        return f"Error: {e}"

def get_current_time() -> str:
    """Get the current date and time."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# --- Tool Registry ---
TOOLS = {
    "search_web": {
        "function": search_web,
        "description": "Search the web for information",
        "parameters": {"query": "string"}
    },
    "calculate": {
        "function": calculate,
        "description": "Evaluate a mathematical expression",
        "parameters": {"expression": "string"}
    },
    "get_current_time": {
        "function": get_current_time,
        "description": "Get the current date and time",
        "parameters": {}
    }
}

# --- Agent System Prompt ---
AGENT_SYSTEM_PROMPT = """You are an AI agent that can use tools to answer questions.

Available tools:
{tools}

When you need to use a tool, respond with EXACTLY this JSON format:
{{"action": "tool_name", "input": "tool input string"}}

When you have the final answer and don't need any more tools, respond with:
{{"action": "final_answer", "input": "your final answer to the user"}}

RULES:
- Use tools when you need real-time data or calculations
- Always think step by step
- Use only ONE tool per response
- After seeing a tool result, decide if you need another tool or can give the final answer
"""

def build_system_prompt() -> str:
    tools_desc = "\n".join(
        f"- {name}: {info['description']} (params: {info['parameters']})"
        for name, info in TOOLS.items()
    )
    return AGENT_SYSTEM_PROMPT.format(tools=tools_desc)

# --- The Agent ---
class SimpleAgent:
    def __init__(self, model: str = "gpt-4o-mini", max_steps: int = 5):
        self.model = model
        self.max_steps = max_steps
        self.messages = [{"role": "system", "content": build_system_prompt()}]
    
    def _call_llm(self) -> str:
        """Call the LLM and get its response."""
        response = client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            temperature=0,
            max_tokens=500,
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content
    
    def _execute_tool(self, tool_name: str, tool_input: str) -> str:
        """Execute a tool and return its output."""
        if tool_name not in TOOLS:
            return f"Error: Unknown tool '{tool_name}'"
        
        tool = TOOLS[tool_name]
        func = tool["function"]
        
        if tool["parameters"]:
            return func(tool_input)
        else:
            return func()
    
    def run(self, user_message: str) -> str:
        """Run the agent loop."""
        self.messages.append({"role": "user", "content": user_message})
        
        for step in range(self.max_steps):
            print(f"\n--- Step {step + 1} ---")
            
            # THINK: Ask the LLM what to do
            llm_response = self._call_llm()
            print(f"LLM says: {llm_response}")
            
            # Parse the action
            try:
                action = json.loads(llm_response)
            except json.JSONDecodeError:
                print("Failed to parse LLM response as JSON")
                return llm_response
            
            action_name = action.get("action", "")
            action_input = action.get("input", "")
            
            # Check if we have a final answer
            if action_name == "final_answer":
                self.messages.append({"role": "assistant", "content": action_input})
                return action_input
            
            # ACT: Execute the tool
            print(f"Executing tool: {action_name}({action_input})")
            tool_result = self._execute_tool(action_name, action_input)
            print(f"Tool result: {tool_result}")
            
            # PERCEIVE: Add results to conversation
            self.messages.append({"role": "assistant", "content": llm_response})
            self.messages.append({
                "role": "user",
                "content": f"Tool '{action_name}' returned: {tool_result}\n\nBased on this result, decide your next action."
            })
        
        return "Max steps reached. Could not complete the task."

# --- Demo ---
if __name__ == "__main__":
    agent = SimpleAgent()
    
    # Test 1: Direct question
    print("=" * 50)
    result = agent.run("What is 2^10 + 3^5?")
    print(f"\nFinal Answer: {result}")
    
    # Test 2: Question requiring search
    agent2 = SimpleAgent()
    print("\n" + "=" * 50)
    result = agent2.run("What is the latest version of Python?")
    print(f"\nFinal Answer: {result}")
```

---

## 5. Exercises

### Exercise 1: Add More Tools
```python
# Add these tools to the SimpleAgent:
# 1. file_reader(path) — reads a file's contents
# 2. word_counter(text) — counts words in text
# 3. translator(text) — "translates" by upper-casing (mock)
# Test the agent with queries that chain multiple tools
```

### Exercise 2: Agent with Memory
```python
# Modify SimpleAgent to include a memory tool:
# - store_memory(key, value) — saves a fact
# - recall_memory(key) — retrieves a fact
# Test: "Remember that my server IP is 192.168.1.100"
# Then: "What is my server IP?"
```

### Exercise 3: Planning Agent
```python
# Build a PlanningAgent that:
# 1. First creates a plan (list of steps) using the LLM
# 2. Then executes each step one by one
# 3. Reports progress after each step
# 4. Handles failures and replanning
```

---

## Solutions

See [solutions/day22_solutions.py](../solutions/day22_solutions.py)

---

## Key Takeaways
- An agent = LLM + Tools + Loop
- The core loop: Perceive → Think → Act → Check if done
- The ReAct pattern has the LLM reason then act in alternating steps
- JSON-formatted tool calls make parsing reliable
- Always limit max steps to prevent infinite loops
- Error handling in tool execution is critical

**Tomorrow:** Tool use — giving agents real capabilities →
