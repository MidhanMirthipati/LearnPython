# ============================================
# Day 23 Solutions — Tool Use & Function Calling
# ============================================
# Supports OpenAI, Anthropic, and Gemini tool/function calling

import json
import os
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "openai")
HAS_API = False

try:
    if LLM_PROVIDER == "openai":
        from openai import OpenAI
        if os.environ.get("OPENAI_API_KEY"):
            HAS_API = True
    elif LLM_PROVIDER == "anthropic":
        import anthropic
        if os.environ.get("ANTHROPIC_API_KEY"):
            HAS_API = True
    elif LLM_PROVIDER == "gemini":
        import google.generativeai as genai
        if os.environ.get("GOOGLE_API_KEY"):
            genai.configure()
            HAS_API = True
except ImportError:
    pass


# --- Exercise 1: Tool Registry with Schema ---
print("--- Tool Registry with Schema ---")


class ToolRegistry:
    """Registry of tools with LLM-compatible function schemas (OpenAI format)."""

    def __init__(self):
        self._tools: dict[str, dict] = {}

    def register(self, name: str, description: str, parameters: dict, func: callable):
        self._tools[name] = {
            "function": func,
            "schema": {
                "type": "function",
                "function": {
                    "name": name,
                    "description": description,
                    "parameters": parameters,
                },
            },
        }

    def get_schemas(self) -> list[dict]:
        return [t["schema"] for t in self._tools.values()]

    def execute(self, name: str, arguments: dict) -> str:
        if name not in self._tools:
            return json.dumps({"error": f"Tool '{name}' not found"})
        try:
            result = self._tools[name]["function"](**arguments)
            return json.dumps({"result": result})
        except Exception as e:
            return json.dumps({"error": str(e)})

    def list_tools(self) -> list[str]:
        return [f"{name}: {t['schema']['function']['description']}" for name, t in self._tools.items()]


# Define tools
registry = ToolRegistry()

# Weather tool
def get_weather(city: str, units: str = "celsius") -> dict:
    """Simulated weather lookup."""
    temps = {"New York": 22, "London": 15, "Tokyo": 28, "Sydney": 18}
    temp = temps.get(city, 20)
    if units == "fahrenheit":
        temp = temp * 9 / 5 + 32
    return {"city": city, "temperature": temp, "units": units, "condition": "partly cloudy"}

registry.register(
    "get_weather",
    "Get current weather for a city",
    {
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "City name"},
            "units": {"type": "string", "enum": ["celsius", "fahrenheit"], "default": "celsius"},
        },
        "required": ["city"],
    },
    get_weather,
)

# Calculator tool
def calculate(expression: str) -> float:
    """Evaluate a math expression safely."""
    allowed = set("0123456789+-*/.() ")
    if not all(c in allowed for c in expression):
        raise ValueError("Invalid characters in expression")
    return eval(expression)

registry.register(
    "calculate",
    "Evaluate a mathematical expression",
    {
        "type": "object",
        "properties": {
            "expression": {"type": "string", "description": "Math expression to evaluate"},
        },
        "required": ["expression"],
    },
    calculate,
)

# Server status tool
def check_server(hostname: str, port: int = 443) -> dict:
    import random
    status = random.choice(["healthy", "healthy", "healthy", "degraded"])
    return {"hostname": hostname, "port": port, "status": status, "latency_ms": random.randint(10, 200)}

registry.register(
    "check_server",
    "Check the status of a server",
    {
        "type": "object",
        "properties": {
            "hostname": {"type": "string", "description": "Server hostname"},
            "port": {"type": "integer", "description": "Port number", "default": 443},
        },
        "required": ["hostname"],
    },
    check_server,
)

# Show tools
print("Available tools:")
for tool in registry.list_tools():
    print(f"  {tool}")

# Test execution
print("\nTool executions:")
print(f"  weather: {registry.execute('get_weather', {'city': 'London'})}")
print(f"  calc:    {registry.execute('calculate', {'expression': '(100 + 50) * 0.15'})}")
print(f"  server:  {registry.execute('check_server', {'hostname': 'api.example.com'})}")


# --- Exercise 2: Function Calling Loop ---
print("\n--- Function Calling Loop ---")


def function_calling_loop(query: str, registry: ToolRegistry, max_iterations: int = 3):
    """Simulate the function calling loop (with or without API)."""
    print(f"\n  Query: {query}")
    messages = [
        {"role": "system", "content": "You are a helpful assistant with access to tools. Use them when needed."},
        {"role": "user", "content": query},
    ]

    if HAS_API and LLM_PROVIDER == "openai":
        client = OpenAI()

        for i in range(max_iterations):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=registry.get_schemas(),
                tool_choice="auto",
            )

            msg = response.choices[0].message

            if msg.tool_calls:
                messages.append(msg)
                for tool_call in msg.tool_calls:
                    name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments)
                    print(f"  Step {i+1}: Calling {name}({args})")

                    result = registry.execute(name, args)
                    print(f"    Result: {result}")

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result,
                    })
            else:
                print(f"  Final: {msg.content}")
                return msg.content

        return "Max iterations reached."
    else:
        # Simulated function calling
        query_lower = query.lower()
        if "weather" in query_lower:
            result = registry.execute("get_weather", {"city": "London"})
            print(f"  [Simulated] Called get_weather → {result}")
        elif "calculate" in query_lower or any(c.isdigit() for c in query):
            result = registry.execute("calculate", {"expression": "100 * 0.15"})
            print(f"  [Simulated] Called calculate → {result}")
        elif "server" in query_lower or "status" in query_lower:
            result = registry.execute("check_server", {"hostname": "api.example.com"})
            print(f"  [Simulated] Called check_server → {result}")
        else:
            print(f"  [Simulated] No tool needed. Direct answer.")

        return "[Simulated response]"


# Test
function_calling_loop("What's the weather in Tokyo?", registry)
function_calling_loop("Calculate 25% of 840", registry)
function_calling_loop("Check if api.example.com is running", registry)


# --- Exercise 3: Tool Chaining ---
print("\n--- Tool Chaining ---")


class ToolChain:
    """Chain multiple tools together in sequence."""

    def __init__(self, registry: ToolRegistry):
        self.registry = registry
        self.steps: list[dict] = []

    def add_step(self, tool_name: str, args: dict, output_key: str):
        self.steps.append({
            "tool": tool_name,
            "args": args,
            "output_key": output_key,
        })
        return self

    def execute(self) -> dict:
        """Execute all steps, passing outputs forward."""
        context = {}
        results = []

        for i, step in enumerate(self.steps):
            # Substitute context variables in args
            resolved_args = {}
            for key, value in step["args"].items():
                if isinstance(value, str) and value.startswith("$"):
                    resolved_args[key] = context.get(value[1:], value)
                else:
                    resolved_args[key] = value

            result = self.registry.execute(step["tool"], resolved_args)
            parsed = json.loads(result)
            context[step["output_key"]] = parsed.get("result", parsed)

            print(f"  Step {i+1}: {step['tool']}({resolved_args}) → {result[:80]}")
            results.append(parsed)

        return {"steps": len(results), "context": context}


# Test chain
chain = ToolChain(registry)
chain.add_step("get_weather", {"city": "Tokyo"}, "weather")
chain.add_step("check_server", {"hostname": "api.weather.com"}, "server_status")
chain.add_step("calculate", {"expression": "28 * 9 / 5 + 32"}, "temp_fahrenheit")

print("\nExecuting chain:")
result = chain.execute()
print(f"\nChain context: {json.dumps(result['context'], indent=2, default=str)[:300]}")
