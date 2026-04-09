# ============================================
# Day 25 Solutions — LangChain Agents
# ============================================

# NOTE: Requires langchain. Install with:
# pip install langchain langchain-openai langchain-anthropic langchain-google-genai langchain-community

import os
import json
from datetime import datetime

try:
    from langchain_openai import ChatOpenAI
    from langchain.agents import AgentExecutor, create_react_agent
    from langchain.tools import tool
    from langchain.prompts import PromptTemplate
    from dotenv import load_dotenv
    load_dotenv()
    # Works with any configured provider's key
    HAS_LANGCHAIN = bool(
        os.environ.get("OPENAI_API_KEY")
        or os.environ.get("ANTHROPIC_API_KEY")
        or os.environ.get("GOOGLE_API_KEY")
    )
except ImportError:
    HAS_LANGCHAIN = False
    print("[INFO] LangChain not installed or no API key. Using simulated version.\n")


# --- Exercise 1: Custom LangChain Tools ---
print("--- Custom LangChain Tools ---")

if HAS_LANGCHAIN:
    @tool
    def server_status(hostname: str) -> str:
        """Check the status of a server by hostname."""
        import random
        status = random.choice(["healthy", "healthy", "degraded"])
        latency = random.randint(10, 200)
        return json.dumps({"hostname": hostname, "status": status, "latency_ms": latency})

    @tool
    def docker_info(container_name: str) -> str:
        """Get info about a Docker container."""
        import random
        return json.dumps({
            "name": container_name,
            "status": random.choice(["running", "stopped", "restarting"]),
            "cpu_pct": round(random.uniform(0, 80), 1),
            "memory_mb": random.randint(50, 512),
            "uptime": f"{random.randint(1, 72)}h",
        })

    @tool
    def calculate_cost(model: str, tokens: int) -> str:
        """Calculate the cost of using an AI model for a given number of tokens."""
        rates = {
            "gpt-4": 0.03, "gpt-4o": 0.005, "gpt-4o-mini": 0.00015,
            "claude-sonnet": 0.003, "claude-haiku": 0.00025,
            "gemini-flash": 0.000075, "gemini-pro": 0.00125,
        }
        rate = rates.get(model, 0.002)
        cost = (tokens / 1000) * rate
        return json.dumps({"model": model, "tokens": tokens, "cost": f"${cost:.4f}"})

    tools = [server_status, docker_info, calculate_cost]

    # Create ReAct agent
    # LangChain supports multiple providers — swap the LLM line as needed:
    #   from langchain_anthropic import ChatAnthropic
    #   llm = ChatAnthropic(model="claude-sonnet-4-20250514", temperature=0)
    #   from langchain_google_genai import ChatGoogleGenerativeAI
    #   llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    prompt = PromptTemplate.from_template(
        """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}"""
    )

    agent = create_react_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools, verbose=True, max_iterations=3)

    # Test
    result = executor.invoke({"input": "Check the status of api.example.com and tell me if it's healthy"})
    print(f"\nResult: {result['output']}")

else:
    # Simulated version
    print("Simulated LangChain tools:")

    class SimTool:
        def __init__(self, name, description, func):
            self.name = name
            self.description = description
            self.func = func

        def run(self, query: str) -> str:
            return self.func(query)

    tools = [
        SimTool("server_status", "Check server health", lambda h: json.dumps({"hostname": h, "status": "healthy", "latency_ms": 45})),
        SimTool("docker_info", "Get container info", lambda c: json.dumps({"name": c, "status": "running", "cpu_pct": 15.2})),
        SimTool("calculate_cost", "Calculate AI model cost", lambda q: json.dumps({"cost": "$0.0150"})),
    ]

    for tool in tools:
        print(f"  {tool.name}: {tool.description}")
        print(f"    Test: {tool.run('test-input')}")


# --- Exercise 2: Agent with Memory ---
print("\n--- Agent with Memory ---")


class SimpleMemoryAgent:
    """A simulated LangChain-style agent with memory."""

    def __init__(self):
        self.memory: list[dict] = []
        self.facts: dict[str, str] = {}
        self.tools = {
            "remember": self._remember,
            "recall": self._recall,
            "search": lambda q: f"Found results for: {q}",
            "calculate": lambda expr: str(eval(expr)) if expr.replace(".", "").replace("+", "").replace("-", "").replace("*", "").replace("/", "").replace(" ", "").isdigit() or True else "Error",
        }

    def _remember(self, fact: str) -> str:
        parts = fact.split(":", 1)
        if len(parts) == 2:
            key, value = parts[0].strip(), parts[1].strip()
            self.facts[key] = value
            return f"Remembered: {key} = {value}"
        return "Use format 'key: value'"

    def _recall(self, key: str) -> str:
        key = key.strip()
        if key in self.facts:
            return f"{key}: {self.facts[key]}"
        # Search for partial matches
        matches = {k: v for k, v in self.facts.items() if key.lower() in k.lower()}
        if matches:
            return json.dumps(matches)
        return f"No memory found for '{key}'"

    def chat(self, message: str) -> str:
        self.memory.append({"role": "user", "content": message, "time": datetime.now().isoformat()})

        # Simple routing
        msg_lower = message.lower()
        if "remember" in msg_lower:
            fact = message.split("remember", 1)[1].strip().lstrip("that").strip()
            response = self._remember(fact)
        elif "recall" in msg_lower or "what do you know" in msg_lower:
            query = message.split("about", 1)[1].strip() if "about" in message else message
            response = self._recall(query)
        else:
            response = f"I understand. You said: '{message[:50]}'. I have {len(self.facts)} stored facts."

        self.memory.append({"role": "assistant", "content": response, "time": datetime.now().isoformat()})
        return response


# Test
agent = SimpleMemoryAgent()
print(agent.chat("Remember that server: api.prod.example.com"))
print(agent.chat("Remember that deploy_day: Friday"))
print(agent.chat("Remember that team_lead: Alice"))
print(agent.chat("What do you know about server"))
print(agent.chat("Recall deploy_day"))
print(agent.chat("What is the meaning of life?"))


# --- Exercise 3: Multi-Tool Agent ---
print("\n--- Multi-Tool Agent ---")


class MultiToolAgent:
    """Agent that selects and chains tools based on the query."""

    def __init__(self):
        self.tools = {}
        self.execution_log: list[dict] = []

    def add_tool(self, name: str, func: callable, keywords: list[str]):
        self.tools[name] = {"func": func, "keywords": keywords}

    def _select_tools(self, query: str) -> list[str]:
        """Select tools based on keyword matching."""
        query_lower = query.lower()
        selected = []
        for name, tool in self.tools.items():
            if any(kw in query_lower for kw in tool["keywords"]):
                selected.append(name)
        return selected or ["default"]

    def execute(self, query: str) -> dict:
        selected = self._select_tools(query)
        results = {}

        print(f"  Query: {query}")
        print(f"  Selected tools: {selected}")

        for tool_name in selected:
            if tool_name in self.tools:
                try:
                    result = self.tools[tool_name]["func"](query)
                    results[tool_name] = result
                    print(f"    {tool_name}: {result}")
                except Exception as e:
                    results[tool_name] = f"Error: {e}"
            else:
                results[tool_name] = "No specific tool matched. Providing general response."

        self.execution_log.append({
            "query": query,
            "tools_used": selected,
            "results": results,
            "timestamp": datetime.now().isoformat(),
        })

        return results


# Build agent
multi_agent = MultiToolAgent()
multi_agent.add_tool("weather", lambda q: json.dumps({"temp": 22, "condition": "sunny"}), ["weather", "temperature"])
multi_agent.add_tool("server", lambda q: json.dumps({"status": "healthy"}), ["server", "status", "health"])
multi_agent.add_tool("deploy", lambda q: json.dumps({"deployed": True, "version": "v2.1"}), ["deploy", "release", "ship"])
multi_agent.add_tool("logs", lambda q: json.dumps({"errors": 3, "warnings": 12}), ["log", "error", "debug"])

# Test
print()
multi_agent.execute("What's the weather like?")
print()
multi_agent.execute("Check the server health and deploy status")
print()
multi_agent.execute("Show me error logs")
print()
multi_agent.execute("Hello, how are you?")
