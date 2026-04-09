# ============================================
# Capstone Project — DevOps Assistant Agent
# Agents Module
# ============================================

import json
import os
from datetime import datetime

from . import config
from .tools import ToolRegistry, create_default_registry
from .memory import ConversationMemory
from .guardrails import GuardrailSystem
from .logger import AgentLogger

try:
    from openai import OpenAI
    HAS_OPENAI = bool(os.environ.get("OPENAI_API_KEY"))
except ImportError:
    HAS_OPENAI = False

try:
    import anthropic
    HAS_ANTHROPIC = bool(os.environ.get("ANTHROPIC_API_KEY"))
except ImportError:
    HAS_ANTHROPIC = False

try:
    import google.generativeai as genai
    HAS_GEMINI = bool(os.environ.get("GOOGLE_API_KEY"))
    if HAS_GEMINI:
        genai.configure()
except ImportError:
    HAS_GEMINI = False

HAS_API = HAS_OPENAI or HAS_ANTHROPIC or HAS_GEMINI


class DevOpsAgent:
    """The main DevOps Assistant Agent with tools, memory, and guardrails."""

    def __init__(self):
        self.registry = create_default_registry()
        self.memory = ConversationMemory(
            max_messages=config.MEMORY_WINDOW_SIZE,
            token_budget=config.TOKEN_BUDGET,
        )
        self.guardrails = GuardrailSystem(blocked_patterns=config.BLOCKED_PATTERNS)
        self.logger = AgentLogger(log_dir=str(config.LOG_DIR), level=config.LOG_LEVEL)
        self.use_api = HAS_API
        self.provider = config.LLM_PROVIDER

        if self.use_api:
            if self.provider == "openai" and HAS_OPENAI:
                self.client = OpenAI()
            elif self.provider == "anthropic" and HAS_ANTHROPIC:
                self.client = anthropic.Anthropic()
            elif self.provider == "gemini" and HAS_GEMINI:
                self.client = genai.GenerativeModel(config.MODEL)
            else:
                self.use_api = False
            self.logger.info("agent", f"Initialized with {self.provider}. Model: {config.MODEL}")
        else:
            self.client = None
            self.logger.info("agent", "Initialized in simulation mode (no API key)")

    def chat(self, user_message: str) -> str:
        """Process a user message through the full agent pipeline."""

        # 1. Input guardrails
        input_check = self.guardrails.check_input(user_message)
        if not input_check["safe"]:
            self.logger.warning("guardrails", f"Input blocked: {input_check['issues']}")
            return f"I can't process that input. Issues: {', '.join(input_check['issues'])}"

        sanitized = input_check["sanitized_input"]

        # 2. Add to memory
        self.memory.add_message("user", sanitized)
        self.logger.debug("memory", f"Added user message ({len(sanitized)} chars)")

        # 3. Generate response
        if self.use_api:
            response = self._api_response(sanitized)
        else:
            response = self._simulated_response(sanitized)

        # 4. Output guardrails
        output_check = self.guardrails.check_output(response)
        final_response = output_check["output"]
        if not output_check["safe"]:
            self.logger.warning("guardrails", f"Output modified: {output_check['issues']}")

        # 5. Add response to memory
        self.memory.add_message("assistant", final_response)

        return final_response

    def _api_response(self, user_message: str) -> str:
        """Generate response using the configured LLM provider."""
        if self.provider == "openai":
            return self._openai_response(user_message)
        elif self.provider == "anthropic":
            return self._anthropic_response(user_message)
        elif self.provider == "gemini":
            return self._gemini_response(user_message)
        return self._simulated_response(user_message)

    def _openai_response(self, user_message: str) -> str:
        """Generate response using OpenAI API with function calling."""
        context = self.memory.build_context(config.SYSTEM_PROMPT)

        for step in range(config.MAX_AGENT_STEPS):
            start = datetime.now()
            response = self.client.chat.completions.create(
                model=config.MODEL,
                messages=context,
                tools=self.registry.get_schemas(),
                tool_choice="auto",
                temperature=config.TEMPERATURE,
                max_tokens=config.MAX_TOKENS,
            )
            elapsed_ms = int((datetime.now() - start).total_seconds() * 1000)
            tokens = response.usage.total_tokens if response.usage else 0
            self.logger.log_llm_call(config.MODEL, tokens, elapsed_ms)

            msg = response.choices[0].message

            # If tool calls, execute them
            if msg.tool_calls:
                context.append(msg)
                for tool_call in msg.tool_calls:
                    name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments)

                    self.logger.log_tool_call(name, args, "")
                    result = self.registry.execute(name, args)
                    self.logger.debug("tools", f"Result: {result[:100]}")

                    context.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result,
                    })
            else:
                return msg.content or "I don't have a response for that."

        return "I reached my step limit. Please try a simpler request."

    def _anthropic_response(self, user_message: str) -> str:
        """Generate response using Anthropic Claude API."""
        messages = self.memory.get_recent_messages()
        start = datetime.now()
        response = self.client.messages.create(
            model=config.MODEL,
            max_tokens=config.MAX_TOKENS,
            system=config.SYSTEM_PROMPT,
            messages=messages,
            temperature=config.TEMPERATURE,
        )
        elapsed_ms = int((datetime.now() - start).total_seconds() * 1000)
        tokens = response.usage.input_tokens + response.usage.output_tokens
        self.logger.log_llm_call(config.MODEL, tokens, elapsed_ms)
        return response.content[0].text if response.content else "No response."

    def _gemini_response(self, user_message: str) -> str:
        """Generate response using Google Gemini API."""
        start = datetime.now()
        response = self.client.generate_content(
            f"{config.SYSTEM_PROMPT}\n\nUser: {user_message}",
            generation_config={
                "temperature": config.TEMPERATURE,
                "max_output_tokens": config.MAX_TOKENS,
            },
        )
        elapsed_ms = int((datetime.now() - start).total_seconds() * 1000)
        tokens = response.usage_metadata.total_token_count if response.usage_metadata else 0
        self.logger.log_llm_call(config.MODEL, tokens, elapsed_ms)
        return response.text

    def _simulated_response(self, user_message: str) -> str:
        """Generate a simulated response with tool use."""
        msg_lower = user_message.lower()

        # Route to tools based on keywords
        if any(kw in msg_lower for kw in ["server", "health", "status", "ping"]):
            hostname = "api.example.com"
            # Try to extract hostname from message
            words = user_message.split()
            for word in words:
                if "." in word and len(word) > 3:
                    hostname = word.strip("?.,!")
                    break
            result = self.registry.execute("check_server", {"hostname": hostname})
            parsed = json.loads(result)
            self.logger.log_tool_call("check_server", {"hostname": hostname}, result)
            return f"Server Status for {parsed.get('hostname', hostname)}:\n" \
                   f"  Status: {parsed.get('status', 'unknown')}\n" \
                   f"  Latency: {parsed.get('latency_ms', 'N/A')}ms\n" \
                   f"  Uptime: {parsed.get('uptime', 'N/A')}"

        elif any(kw in msg_lower for kw in ["docker", "container"]):
            result = self.registry.execute("docker_status", {"container_name": "all"})
            parsed = json.loads(result)
            self.logger.log_tool_call("docker_status", {}, result)
            lines = ["Docker Container Status:"]
            for name, info in parsed.get("containers", {}).items():
                emoji = "🟢" if info["status"] == "running" else "🔴"
                lines.append(f"  {emoji} {name}: {info['status']} (CPU: {info['cpu']}, Mem: {info['memory']})")
            return "\n".join(lines)

        elif any(kw in msg_lower for kw in ["kubernetes", "k8s", "pod", "cluster"]):
            result = self.registry.execute("k8s_info", {"namespace": "default"})
            parsed = json.loads(result)
            self.logger.log_tool_call("k8s_info", {}, result)
            lines = [f"Kubernetes Cluster ({parsed['namespace']} namespace):"]
            lines.append(f"  Nodes: {parsed['nodes']}, Pods: {parsed['total_pods']}")
            for pod in parsed.get("pods", []):
                emoji = "🟢" if pod["status"] == "Running" else "🔴"
                lines.append(f"  {emoji} {pod['name']}: {pod['status']} (restarts: {pod['restarts']})")
            return "\n".join(lines)

        elif any(kw in msg_lower for kw in ["pipeline", "ci/cd", "ci", "cd", "build"]):
            result = self.registry.execute("ci_pipeline", {"repo": "main"})
            parsed = json.loads(result)
            self.logger.log_tool_call("ci_pipeline", {}, result)
            lines = [f"CI/CD Pipeline ({parsed['repo']}): {parsed['status']}"]
            for stage in parsed.get("stages", []):
                emoji = "✅" if stage["status"] == "passed" else "❌"
                lines.append(f"  {emoji} {stage['name']}: {stage['status']}")
            lines.append(f"  Duration: {parsed['duration']}")
            return "\n".join(lines)

        elif any(kw in msg_lower for kw in ["log", "error", "debug"]):
            service = "api"
            for word in user_message.split():
                if word.lower() not in ["show", "me", "the", "logs", "for", "errors", "error", "log", "check", "analyze"]:
                    service = word.strip("?.,!")
                    break
            result = self.registry.execute("analyze_logs", {"service": service, "level": "ERROR"})
            parsed = json.loads(result)
            self.logger.log_tool_call("analyze_logs", {"service": service}, result)
            lines = [f"Logs for {parsed['service']} ({parsed['level']}):"]
            for entry in parsed.get("entries", []):
                lines.append(f"  ❌ {entry['message']}")
            lines.append(f"  Total matching: {parsed['total_matching']}")
            return "\n".join(lines)

        elif any(kw in msg_lower for kw in ["cost", "budget", "billing", "spend"]):
            result = self.registry.execute("calculate_cost", {"service": "production", "hours": 24})
            parsed = json.loads(result)
            self.logger.log_tool_call("calculate_cost", {}, result)
            lines = [f"Cost Estimate ({parsed['service']}, {parsed['period_hours']}h):"]
            for k, v in parsed.get("breakdown", {}).items():
                lines.append(f"  {k}: ${v}")
            lines.append(f"  Total: {parsed['total']}")
            lines.append(f"  Monthly projection: {parsed['projected_monthly']}")
            return "\n".join(lines)

        elif any(kw in msg_lower for kw in ["help", "what can you do", "tools"]):
            tools = self.registry.list_tools()
            lines = ["I can help with the following:"]
            for tool in tools:
                lines.append(f"  🔧 {tool['name']}: {tool['description']}")
            lines.append("\nJust ask me about any DevOps topic!")
            return "\n".join(lines)

        else:
            return (f"I'm your DevOps Assistant! I can help with server monitoring, "
                    f"Docker, Kubernetes, CI/CD pipelines, log analysis, and cost estimation. "
                    f"Try asking about any of these topics, or type 'help' for a list of capabilities.")

    def handle_command(self, command: str) -> str | None:
        """Handle special / commands. Returns response or None if not a command."""
        parts = command.split(maxsplit=1)
        cmd = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        if cmd == "/help":
            return """Available commands:
  /help       — Show this help
  /tools      — List available tools
  /memory     — Show memory stats
  /facts      — Show stored facts
  /remember   — Store a fact (e.g., /remember server: api.prod.com)
  /stats      — Show session statistics
  /clear      — Clear conversation history
  /quit       — Exit with session summary"""

        elif cmd == "/tools":
            tools = self.registry.list_tools()
            return "\n".join(f"  🔧 {t['name']}: {t['description']}" for t in tools)

        elif cmd == "/memory":
            stats = self.memory.get_stats()
            return "\n".join(f"  {k}: {v}" for k, v in stats.items())

        elif cmd == "/facts":
            if self.memory.facts:
                return "\n".join(f"  {k}: {v}" for k, v in self.memory.facts.items())
            return "  No stored facts."

        elif cmd == "/remember":
            if ":" in arg:
                key, _, value = arg.partition(":")
                self.memory.add_fact(key.strip(), value.strip())
                return f"  Remembered: {key.strip()} = {value.strip()}"
            return "  Use format: /remember key: value"

        elif cmd == "/stats":
            lines = ["Session Statistics:"]
            mem = self.memory.get_stats()
            guard = self.guardrails.get_stats()
            log = self.logger.get_summary()
            lines.append(f"  Messages: {mem['total_processed']}")
            lines.append(f"  Tokens: {mem['current_tokens']}/{mem['token_budget']}")
            lines.append(f"  Facts: {mem['stored_facts']}")
            lines.append(f"  Inputs checked: {guard['inputs_checked']}")
            lines.append(f"  Inputs blocked: {guard['inputs_blocked']}")
            lines.append(f"  Log entries: {log['total_entries']}")
            return "\n".join(lines)

        elif cmd == "/clear":
            self.memory.clear()
            return "  Conversation cleared (facts preserved)."

        elif cmd == "/quit":
            return "QUIT"

        return None  # Not a recognized command
