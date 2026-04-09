# ============================================
# Day 27 Solutions — Multi-Agent Systems
# ============================================

import json
from datetime import datetime
from collections import deque


# --- Exercise 1: Agent Communication Protocol ---
print("--- Agent Communication Protocol ---")


class AgentMessage:
    """Message passed between agents."""

    def __init__(self, sender: str, receiver: str, content: str,
                 msg_type: str = "request", priority: int = 5):
        self.id = f"msg_{datetime.now().strftime('%H%M%S%f')}"
        self.sender = sender
        self.receiver = receiver
        self.content = content
        self.type = msg_type  # request, response, broadcast, delegate
        self.priority = priority
        self.timestamp = datetime.now().isoformat()

    def __str__(self):
        return f"[{self.type}] {self.sender} → {self.receiver}: {self.content[:50]}"


class MessageBus:
    """Central message bus for agent communication."""

    def __init__(self):
        self.queues: dict[str, deque[AgentMessage]] = {}
        self.log: list[AgentMessage] = []

    def register(self, agent_name: str):
        self.queues[agent_name] = deque()

    def send(self, message: AgentMessage):
        self.log.append(message)
        if message.receiver == "all":
            for name, queue in self.queues.items():
                if name != message.sender:
                    queue.append(message)
        elif message.receiver in self.queues:
            self.queues[message.receiver].append(message)

    def receive(self, agent_name: str) -> AgentMessage | None:
        if agent_name in self.queues and self.queues[agent_name]:
            return self.queues[agent_name].popleft()
        return None

    def pending_count(self, agent_name: str) -> int:
        return len(self.queues.get(agent_name, []))


# Test
bus = MessageBus()
bus.register("coordinator")
bus.register("researcher")
bus.register("coder")

bus.send(AgentMessage("coordinator", "researcher", "Find info about Docker networking"))
bus.send(AgentMessage("coordinator", "coder", "Write a Dockerfile for Python app"))

msg = bus.receive("researcher")
print(f"Researcher received: {msg}")
bus.send(AgentMessage("researcher", "coordinator", "Found 5 articles on Docker networking", "response"))

msg = bus.receive("coordinator")
print(f"Coordinator received: {msg}")


# --- Exercise 2: Multi-Agent Orchestrator ---
print("\n--- Multi-Agent Orchestrator ---")


class BaseSpecialist:
    """Base class for specialist agents."""

    def __init__(self, name: str, expertise: list[str]):
        self.name = name
        self.expertise = expertise
        self.tasks_completed = 0

    def can_handle(self, task: str) -> bool:
        task_lower = task.lower()
        return any(exp in task_lower for exp in self.expertise)

    def process(self, task: str) -> dict:
        self.tasks_completed += 1
        return {
            "agent": self.name,
            "task": task,
            "result": f"[{self.name}] Processed: {task[:40]}",
            "status": "completed",
        }

    def __str__(self):
        return f"{self.name}(expertise={self.expertise}, completed={self.tasks_completed})"


class ResearchAgent(BaseSpecialist):
    def __init__(self):
        super().__init__("Researcher", ["research", "find", "search", "compare", "analyze"])

    def process(self, task: str) -> dict:
        self.tasks_completed += 1
        return {
            "agent": self.name,
            "task": task,
            "result": f"Research findings: Found 5 relevant sources for '{task[:30]}'",
            "sources": ["doc1.md", "doc2.md"],
            "status": "completed",
        }


class CoderAgent(BaseSpecialist):
    def __init__(self):
        super().__init__("Coder", ["code", "write", "implement", "fix", "debug", "script"])

    def process(self, task: str) -> dict:
        self.tasks_completed += 1
        return {
            "agent": self.name,
            "task": task,
            "result": f"Code generated: ```python\n# Solution for: {task[:30]}\nprint('Done!')\n```",
            "language": "python",
            "status": "completed",
        }


class DevOpsSpecialist(BaseSpecialist):
    def __init__(self):
        super().__init__("DevOps", ["deploy", "docker", "kubernetes", "k8s", "ci/cd", "pipeline", "server", "infra"])

    def process(self, task: str) -> dict:
        self.tasks_completed += 1
        return {
            "agent": self.name,
            "task": task,
            "result": f"DevOps action: Configured deployment for '{task[:30]}'",
            "actions_taken": ["built image", "pushed to registry", "updated deployment"],
            "status": "completed",
        }


class ReviewerAgent(BaseSpecialist):
    def __init__(self):
        super().__init__("Reviewer", ["review", "check", "validate", "test", "verify"])

    def process(self, task: str) -> dict:
        self.tasks_completed += 1
        return {
            "agent": self.name,
            "task": task,
            "result": f"Review complete: {task[:30]} looks good with minor suggestions",
            "issues_found": 1,
            "status": "completed",
        }


class Orchestrator:
    """Coordinates multiple specialist agents."""

    def __init__(self):
        self.agents: list[BaseSpecialist] = []
        self.task_log: list[dict] = []

    def register(self, agent: BaseSpecialist):
        self.agents.append(agent)

    def route(self, task: str) -> BaseSpecialist | None:
        """Find the best agent for a task."""
        for agent in self.agents:
            if agent.can_handle(task):
                return agent
        return None

    def execute(self, task: str) -> dict:
        """Execute a task by routing to the right agent."""
        agent = self.route(task)
        if agent:
            result = agent.process(task)
            self.task_log.append(result)
            return result
        return {"error": f"No agent available for: {task}", "status": "unhandled"}

    def execute_pipeline(self, tasks: list[str]) -> list[dict]:
        """Execute multiple tasks in sequence."""
        results = []
        for task in tasks:
            result = self.execute(task)
            results.append(result)
        return results

    def get_stats(self) -> dict:
        return {
            "agents": {a.name: a.tasks_completed for a in self.agents},
            "total_tasks": len(self.task_log),
            "success": sum(1 for t in self.task_log if t.get("status") == "completed"),
        }


# Test
orch = Orchestrator()
orch.register(ResearchAgent())
orch.register(CoderAgent())
orch.register(DevOpsSpecialist())
orch.register(ReviewerAgent())

tasks = [
    "Research best practices for Docker multi-stage builds",
    "Write a Python script to parse JSON logs",
    "Deploy the application to Kubernetes",
    "Review the pull request for security issues",
    "Find alternatives to Jenkins for CI/CD",
    "Fix the bug in the authentication module",
    "What time is it?",  # No agent for this
]

print("Executing tasks:")
for task in tasks:
    result = orch.execute(task)
    status = result.get("status", "unknown")
    agent = result.get("agent", "none")
    emoji = "✅" if status == "completed" else "❌"
    print(f"  {emoji} [{agent}] {task[:50]}")
    if status != "completed":
        print(f"      → {result.get('error', 'Unknown error')}")

print(f"\nStats: {orch.get_stats()}")


# --- Exercise 3: Collaborative Pipeline ---
print("\n--- Collaborative Pipeline ---")


class CollaborativePipeline:
    """Multi-agent pipeline where agents build on each other's work."""

    def __init__(self, orchestrator: Orchestrator):
        self.orchestrator = orchestrator

    def run(self, goal: str) -> dict:
        """Break a goal into steps and execute collaboratively."""
        print(f"\n  Goal: {goal}")

        # Plan steps based on the goal
        steps = [
            f"Research {goal}",
            f"Write code to implement {goal}",
            f"Deploy the solution for {goal}",
            f"Review and validate the implementation of {goal}",
        ]

        results = []
        context = ""

        for i, step in enumerate(steps):
            print(f"\n  Step {i+1}: {step}")
            result = self.orchestrator.execute(step)
            results.append(result)

            if result.get("status") == "completed":
                context += f"\nStep {i+1} ({result['agent']}): {result['result']}"
                print(f"    ✅ {result['agent']}: {result['result'][:60]}")
            else:
                print(f"    ⚠️ Skipped: {result.get('error', 'No handler')}")

        return {
            "goal": goal,
            "steps_completed": sum(1 for r in results if r.get("status") == "completed"),
            "total_steps": len(steps),
            "results": results,
        }


pipeline = CollaborativePipeline(orch)
outcome = pipeline.run("a microservices API gateway")
print(f"\n  Outcome: {outcome['steps_completed']}/{outcome['total_steps']} steps completed")
