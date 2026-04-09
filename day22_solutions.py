# ============================================
# Day 22 Solutions — Agent Concepts & Architecture
# ============================================

from datetime import datetime


# --- Exercise 1: ReAct Loop Implementation ---
print("--- ReAct Loop ---")


class SimpleAgent:
    """An agent implementing the ReAct (Reason + Act) pattern."""

    def __init__(self, name: str):
        self.name = name
        self.tools: dict[str, callable] = {}
        self.thought_log: list[dict] = []
        self.max_steps = 5

    def register_tool(self, name: str, func: callable, description: str):
        self.tools[name] = {"func": func, "description": description}

    def think(self, observation: str, goal: str) -> dict:
        """Decide next action based on observation."""
        self.thought_log.append({
            "step": len(self.thought_log) + 1,
            "observation": observation,
            "timestamp": datetime.now().isoformat(),
        })

        # Simple keyword matching for tool selection
        obs_lower = observation.lower()
        if "calculate" in obs_lower or any(c.isdigit() for c in observation):
            return {"action": "calculator", "input": observation}
        elif "search" in obs_lower or "find" in obs_lower:
            return {"action": "search", "input": observation}
        elif "done" in obs_lower or "answer" in obs_lower:
            return {"action": "finish", "input": observation}
        else:
            return {"action": "respond", "input": observation}

    def act(self, action: dict) -> str:
        """Execute the chosen action."""
        tool_name = action["action"]

        if tool_name == "finish":
            return f"Final answer: {action['input']}"

        if tool_name == "respond":
            return f"I can help with: {action['input']}"

        if tool_name in self.tools:
            try:
                result = self.tools[tool_name]["func"](action["input"])
                return f"Tool '{tool_name}' returned: {result}"
            except Exception as e:
                return f"Tool '{tool_name}' error: {e}"

        return f"Unknown tool: {tool_name}"

    def run(self, query: str) -> str:
        """Execute the full ReAct loop."""
        print(f"\n  Query: {query}")
        observation = query

        for step in range(self.max_steps):
            # Reason
            thought = self.think(observation, query)
            print(f"  Step {step + 1}:")
            print(f"    Thought: Use '{thought['action']}' tool")

            # Act
            result = self.act(thought)
            print(f"    Result: {result}")

            # Check if done
            if thought["action"] == "finish":
                return result

            observation = result

        return "Reached max steps without a final answer."


# Register tools
agent = SimpleAgent("DevBot")
agent.register_tool("calculator", lambda x: str(eval(x.split("calculate ")[-1])) if "calculate" in x.lower() else "No expression", "Evaluate math")
agent.register_tool("search", lambda x: f"Found 3 results for '{x}'", "Search the web")

# Test
agent.run("Calculate 15 * 8 + 22")
agent.run("Search for Docker best practices")
agent.run("Hello, how are you?")


# --- Exercise 2: Agent State Machine ---
print("\n--- Agent State Machine ---")


class AgentState:
    IDLE = "idle"
    THINKING = "thinking"
    ACTING = "acting"
    WAITING = "waiting"
    ERROR = "error"
    DONE = "done"


class StatefulAgent:
    """Agent with explicit state transitions."""

    VALID_TRANSITIONS = {
        AgentState.IDLE: [AgentState.THINKING],
        AgentState.THINKING: [AgentState.ACTING, AgentState.DONE, AgentState.ERROR],
        AgentState.ACTING: [AgentState.WAITING, AgentState.THINKING, AgentState.ERROR],
        AgentState.WAITING: [AgentState.THINKING, AgentState.ERROR],
        AgentState.ERROR: [AgentState.IDLE],
        AgentState.DONE: [AgentState.IDLE],
    }

    def __init__(self, name: str):
        self.name = name
        self.state = AgentState.IDLE
        self.history: list[dict] = []

    def transition(self, new_state: str):
        if new_state not in self.VALID_TRANSITIONS.get(self.state, []):
            raise ValueError(f"Invalid transition: {self.state} → {new_state}")
        old = self.state
        self.state = new_state
        self.history.append({
            "from": old,
            "to": new_state,
            "time": datetime.now().isoformat(),
        })
        print(f"  {self.name}: {old} → {new_state}")

    def process(self, query: str):
        """Process a query through the state machine."""
        print(f"\n  Processing: '{query}'")
        try:
            self.transition(AgentState.THINKING)
            # Simulate thinking
            thought = f"I should answer: {query}"

            self.transition(AgentState.ACTING)
            # Simulate acting
            result = f"Here's my answer to '{query[:30]}'"

            self.transition(AgentState.THINKING)
            # Evaluate result

            self.transition(AgentState.DONE)
            print(f"  Result: {result}")

        except ValueError as e:
            print(f"  State error: {e}")
            self.state = AgentState.ERROR
            self.transition(AgentState.IDLE)

    def show_history(self):
        print(f"\n  State history for {self.name}:")
        for entry in self.history:
            print(f"    {entry['from']} → {entry['to']}")


# Test
agent = StatefulAgent("StateBot")
agent.process("What is Kubernetes?")
agent.show_history()


# --- Exercise 3: Planning Agent ---
print("\n--- Planning Agent ---")


class PlanStep:
    def __init__(self, action: str, tool: str, depends_on: list[int] | None = None):
        self.action = action
        self.tool = tool
        self.depends_on = depends_on or []
        self.status = "pending"
        self.result = None

    def __str__(self):
        deps = f" (depends on: {self.depends_on})" if self.depends_on else ""
        return f"[{self.status}] {self.action} ({self.tool}){deps}"


class PlanningAgent:
    """An agent that creates and executes plans."""

    def __init__(self):
        self.tools = {
            "search": lambda q: f"Found info about {q}",
            "analyze": lambda d: f"Analysis of {d}: positive outlook",
            "summarize": lambda t: f"Summary: {t[:30]}...",
            "report": lambda d: f"Report generated for {d}",
        }

    def create_plan(self, goal: str) -> list[PlanStep]:
        """Create a multi-step plan for a goal."""
        # Simple planning logic based on keywords
        steps = []
        steps.append(PlanStep(f"Research: {goal}", "search"))
        steps.append(PlanStep(f"Analyze findings", "analyze", depends_on=[0]))
        steps.append(PlanStep(f"Summarize results", "summarize", depends_on=[1]))
        steps.append(PlanStep(f"Generate final report", "report", depends_on=[2]))
        return steps

    def execute_plan(self, steps: list[PlanStep]):
        """Execute a plan respecting dependencies."""
        print(f"\n  Plan ({len(steps)} steps):")
        for i, step in enumerate(steps):
            print(f"    {i}: {step}")

        print(f"\n  Executing:")
        for i, step in enumerate(steps):
            # Check dependencies
            for dep in step.depends_on:
                if steps[dep].status != "completed":
                    step.status = "blocked"
                    print(f"    ❌ Step {i} blocked by step {dep}")
                    continue

            # Execute
            tool = self.tools.get(step.tool)
            if tool:
                step.result = tool(step.action)
                step.status = "completed"
                print(f"    ✅ Step {i}: {step.result}")
            else:
                step.status = "failed"
                print(f"    ❌ Step {i}: Tool '{step.tool}' not found")


# Test
planner = PlanningAgent()
plan = planner.create_plan("Evaluate Docker vs Kubernetes for our use case")
planner.execute_plan(plan)
