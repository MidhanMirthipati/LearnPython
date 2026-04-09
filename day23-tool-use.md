# Day 23: Tool Use — Giving Agents Capabilities

## Learning Goals
- Understand function/tool calling across OpenAI, Anthropic, and Gemini
- Define tools with JSON schemas
- Build practical tools for DevOps agents
- Handle tool call responses correctly for each provider

---

## 1. Defining Tools (Same for All Providers)

All three LLM providers support function calling — the concept is the same, but the format differs slightly. Here are the same two tools defined for each:

### Tool Implementations (shared)
```python
import json

def get_server_status(hostname: str) -> dict:
    """Simulate checking server status."""
    statuses = {
        "web-01": {"status": "healthy", "cpu": 45, "memory": 62, "uptime": "15d"},
        "db-01": {"status": "warning", "cpu": 88, "memory": 91, "uptime": "5d"},
        "api-01": {"status": "healthy", "cpu": 32, "memory": 55, "uptime": "30d"},
    }
    return statuses.get(hostname, {"status": "unknown", "error": f"Host '{hostname}' not found"})

def search_logs(service: str, pattern: str, severity: str = None) -> dict:
    """Simulate log search."""
    logs = [
        {"time": "10:01", "level": "ERROR", "message": f"[{service}] Connection timeout to database"},
        {"time": "10:05", "level": "INFO", "message": f"[{service}] Retry successful"},
        {"time": "10:10", "level": "WARNING", "message": f"[{service}] High memory usage: 91%"},
    ]
    if severity:
        logs = [l for l in logs if l["level"] == severity]
    return {"service": service, "pattern": pattern, "results": logs, "count": len(logs)}

TOOL_MAP = {
    "get_server_status": get_server_status,
    "search_logs": search_logs,
}
```

### OpenAI Tool Schemas
```python
openai_tools = [
    {
        "type": "function",
        "function": {
            "name": "get_server_status",
            "description": "Check the status of a server by hostname or IP",
            "parameters": {
                "type": "object",
                "properties": {
                    "hostname": {"type": "string", "description": "The server hostname or IP address"}
                },
                "required": ["hostname"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_logs",
            "description": "Search application logs for a pattern",
            "parameters": {
                "type": "object",
                "properties": {
                    "service": {"type": "string", "description": "The service name"},
                    "pattern": {"type": "string", "description": "Search pattern or keyword"},
                    "severity": {"type": "string", "enum": ["INFO", "WARNING", "ERROR", "CRITICAL"]}
                },
                "required": ["service", "pattern"]
            }
        }
    }
]
```

### Anthropic Tool Schemas
```python
anthropic_tools = [
    {
        "name": "get_server_status",
        "description": "Check the status of a server by hostname or IP",
        "input_schema": {
            "type": "object",
            "properties": {
                "hostname": {"type": "string", "description": "The server hostname or IP address"}
            },
            "required": ["hostname"]
        }
    },
    {
        "name": "search_logs",
        "description": "Search application logs for a pattern",
        "input_schema": {
            "type": "object",
            "properties": {
                "service": {"type": "string", "description": "The service name"},
                "pattern": {"type": "string", "description": "Search pattern or keyword"},
                "severity": {"type": "string", "enum": ["INFO", "WARNING", "ERROR", "CRITICAL"]}
            },
            "required": ["service", "pattern"]
        }
    }
]
```

### Gemini Tool Schemas
```python
import google.generativeai as genai

gemini_tools = [
    genai.protos.Tool(
        function_declarations=[
            genai.protos.FunctionDeclaration(
                name="get_server_status",
                description="Check the status of a server by hostname or IP",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "hostname": genai.protos.Schema(type=genai.protos.Type.STRING, description="The server hostname or IP address")
                    },
                    required=["hostname"]
                )
            ),
            genai.protos.FunctionDeclaration(
                name="search_logs",
                description="Search application logs for a pattern",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "service": genai.protos.Schema(type=genai.protos.Type.STRING, description="The service name"),
                        "pattern": genai.protos.Schema(type=genai.protos.Type.STRING, description="Search pattern or keyword"),
                        "severity": genai.protos.Schema(type=genai.protos.Type.STRING, description="Log severity level")
                    },
                    required=["service", "pattern"]
                )
            )
        ]
    )
]
```

---

## 2. Agent Loop with Tool Calling

### OpenAI Agent Loop
```python
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()
}

def execute_tool_call_openai(tool_call) -> str:
    """Execute a tool call from the OpenAI response."""
    func_name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)
    if func_name in TOOL_MAP:
        return json.dumps(TOOL_MAP[func_name](**args))
    return json.dumps({"error": f"Unknown tool: {func_name}"})

def agent_chat_openai(user_message: str) -> str:
    """OpenAI agent with function calling support."""
    messages = [
        {"role": "system", "content": "You are a DevOps monitoring assistant. Use tools to check systems and logs."},
        {"role": "user", "content": user_message}
    ]
    while True:
        response = client.chat.completions.create(
            model="gpt-4o-mini", messages=messages,
            tools=openai_tools, tool_choice="auto"
        )
        message = response.choices[0].message
        if not message.tool_calls:
            return message.content
        messages.append(message)
        for tool_call in message.tool_calls:
            print(f"  🔧 Calling: {tool_call.function.name}({tool_call.function.arguments})")
            result = execute_tool_call_openai(tool_call)
            messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": result})

answer = agent_chat_openai("Is the database server db-01 healthy? Also check its logs for errors.")
print(f"\nAgent: {answer}")
```

### Anthropic Agent Loop
```python
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

def agent_chat_anthropic(user_message: str) -> str:
    """Anthropic agent with tool use support."""
    messages = [{"role": "user", "content": user_message}]
    
    while True:
        response = client.messages.create(
            model="claude-sonnet-4-20250514", max_tokens=1024,
            system="You are a DevOps monitoring assistant. Use tools to check systems and logs.",
            messages=messages,
            tools=anthropic_tools  # Uses the Anthropic schema from section 1
        )
        
        # Check if the model wants to use tools
        if response.stop_reason != "tool_use":
            # Extract text response
            return "".join(block.text for block in response.content if block.type == "text")
        
        # Process tool calls
        messages.append({"role": "assistant", "content": response.content})
        
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                print(f"  🔧 Calling: {block.name}({json.dumps(block.input)})")
                func = TOOL_MAP.get(block.name)
                result = json.dumps(func(**block.input)) if func else json.dumps({"error": "Unknown tool"})
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result
                })
        
        messages.append({"role": "user", "content": tool_results})

answer = agent_chat_anthropic("Is the database server db-01 healthy? Also check its logs for errors.")
print(f"\nAgent: {answer}")
```

### Gemini Agent Loop
```python
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure()

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    system_instruction="You are a DevOps monitoring assistant. Use tools to check systems and logs.",
    tools=gemini_tools  # Uses the Gemini schema from section 1
)

def agent_chat_gemini(user_message: str) -> str:
    """Gemini agent with function calling support."""
    chat = model.start_chat()
    response = chat.send_message(user_message)
    
    while response.candidates[0].content.parts:
        # Check for function calls
        function_calls = [p for p in response.candidates[0].content.parts if p.function_call.name]
        if not function_calls:
            return response.text
        
        # Execute each function call
        responses = []
        for part in function_calls:
            fc = part.function_call
            print(f"  🔧 Calling: {fc.name}({dict(fc.args)})")
            func = TOOL_MAP.get(fc.name)
            result = func(**dict(fc.args)) if func else {"error": "Unknown tool"}
            responses.append(
                genai.protos.Part(function_response=genai.protos.FunctionResponse(
                    name=fc.name, response={"result": result}
                ))
            )
        
        response = chat.send_message(genai.protos.Content(parts=responses))
    
    return response.text

answer = agent_chat_gemini("Is the database server db-01 healthy? Also check its logs for errors.")
print(f"\nAgent: {answer}")
```

---

## 3. Building Practical DevOps Tools

```python
import subprocess
import json
from datetime import datetime

class DevOpsToolkit:
    """A collection of practical DevOps tools for an AI agent."""
    
    @staticmethod
    def check_disk_space() -> dict:
        """Check disk space on the current machine."""
        try:
            import shutil
            total, used, free = shutil.disk_usage("/")
            return {
                "total_gb": round(total / (2**30), 2),
                "used_gb": round(used / (2**30), 2),
                "free_gb": round(free / (2**30), 2),
                "usage_percent": round(used / total * 100, 1)
            }
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def run_command(command: str) -> dict:
        """Run a shell command safely (whitelist approach)."""
        # Only allow safe, read-only commands
        allowed_prefixes = ["echo", "date", "hostname", "whoami", "python --version"]
        
        if not any(command.startswith(prefix) for prefix in allowed_prefixes):
            return {"error": f"Command not in allowlist: {command}"}
        
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True,
                text=True, timeout=10
            )
            return {
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"error": "Command timed out (10s limit)"}
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def parse_yaml(yaml_string: str) -> dict:
        """Validate and parse YAML content."""
        try:
            import yaml
            parsed = yaml.safe_load(yaml_string)
            return {"valid": True, "parsed": parsed}
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    @staticmethod
    def generate_dockerfile(language: str, app_type: str = "web") -> str:
        """Generate a basic Dockerfile."""
        templates = {
            ("python", "web"): """FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0"]""",
            
            ("node", "web"): """FROM node:20-slim
WORKDIR /app
COPY package*.json .
RUN npm ci --only=production
COPY . .
EXPOSE 3000
CMD ["node", "server.js"]""",
        }
        
        key = (language.lower(), app_type.lower())
        return templates.get(key, f"# No template for {language}/{app_type}")
    
    @staticmethod
    def health_check(service_url: str) -> dict:
        """Check if a service is responding."""
        import requests
        try:
            start = datetime.now()
            response = requests.get(service_url, timeout=5)
            elapsed = (datetime.now() - start).total_seconds()
            return {
                "url": service_url,
                "status_code": response.status_code,
                "healthy": response.status_code < 400,
                "response_time_ms": round(elapsed * 1000, 1)
            }
        except requests.exceptions.ConnectionError:
            return {"url": service_url, "healthy": False, "error": "Connection refused"}
        except requests.exceptions.Timeout:
            return {"url": service_url, "healthy": False, "error": "Timeout"}

# Tool definitions for OpenAI (see section 1 for Anthropic/Gemini equivalents)
DEVOPS_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "check_disk_space",
            "description": "Check disk space on the current server",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Run a safe, read-only shell command",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "The command to run"}
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_dockerfile",
            "description": "Generate a Dockerfile for a given language and app type",
            "parameters": {
                "type": "object",
                "properties": {
                    "language": {"type": "string", "description": "Programming language (python, node)"},
                    "app_type": {"type": "string", "description": "Application type (web, api, worker)"}
                },
                "required": ["language"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "health_check",
            "description": "Check if a web service is healthy",
            "parameters": {
                "type": "object",
                "properties": {
                    "service_url": {"type": "string", "description": "The URL to check"}
                },
                "required": ["service_url"]
            }
        }
    }
]
```

---

## 4. Exercises

### Exercise 1: Build 3 Custom Tools
```python
# Create 3 tools with schemas for ALL 3 providers (OpenAI, Anthropic, Gemini):
# 1. json_validator(json_string) — validates JSON syntax
# 2. base64_converter(text, mode="encode|decode")
# 3. timestamp_converter(timestamp, from_format, to_format)
# Wire them into the agent loop for your preferred provider
```

### Exercise 2: Tool Chaining Agent
```python
# Build an agent that can chain tools:
# "Generate a Dockerfile for Python, then validate its syntax"
# The agent should:
# 1. Call generate_dockerfile
# 2. Take the output and pass it to a yaml/dockerfile validator
# 3. Report the combined result
```

### Exercise 3: Safe Command Runner
```python
# Build a command execution tool with:
# 1. An allowlist of safe commands
# 2. Input sanitization (no pipes, redirects, or semicolons)
# 3. Timeout protection
# 4. Output size limiting
# 5. Audit logging (record all commands run)
# Test with both safe and unsafe inputs
```

---

## Solutions

See [solutions/day23_solutions.py](../solutions/day23_solutions.py)

---

## Key Takeaways
- All three major LLM providers (OpenAI, Anthropic, Gemini) support function/tool calling
- **OpenAI** uses `tools=` param with `type: "function"` wrapper and returns `tool_calls`
- **Anthropic** uses `tools=` with `input_schema` and returns `tool_use` content blocks
- **Gemini** uses `genai.protos.Tool` with `FunctionDeclaration` and returns `function_call` parts
- Tool implementations are the same — only the schema format and response handling differ
- The LLM decides when and which tools to call
- Always validate and sanitize tool inputs
- Keep tools focused — one tool, one job
- Security: use allowlists, never run arbitrary commands

**Tomorrow:** Memory and state management for agents →
