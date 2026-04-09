# Day 27: Multi-Agent Systems

## Learning Goals
- Understand why multiple agents can be better than one
- Build agents that delegate to specialized sub-agents
- Implement agent communication patterns
- Create a team of cooperating agents

---

## 1. Why Multi-Agent?

| Single Agent | Multi-Agent |
|-------------|-------------|
| One prompt does everything | Specialized prompts per role |
| Complex system prompt | Simple, focused prompts |
| Tool overload | Each agent has relevant tools |
| Hard to debug | Debug one agent at a time |
| Limited expertise | Deep expertise per agent |

---

## 2. Multi-Agent Patterns

### Pattern 1: Router (Dispatcher)
```
User → [Router Agent] → DevOps Agent
                       → Code Agent
                       → Data Agent
```

### Pattern 2: Pipeline (Sequential)
```
User → [Analyzer] → [Planner] → [Implementer] → [Reviewer]
```

### Pattern 3: Debate (Collaborative)
```
User → [Agent A proposes] → [Agent B critiques] → [Agent A refines] → Final
```

### Pattern 4: Supervisor
```
User → [Supervisor] ←→ [Worker 1]
                    ←→ [Worker 2]
                    ←→ [Worker 3]
```

---

## 3. Building a Router Agent

```python
from openai import OpenAI  # Using OpenAI here; see Day 17 for Anthropic/Gemini equivalents
from dotenv import load_dotenv
import json

load_dotenv()
client = OpenAI()

class SpecialistAgent:
    """A specialist agent focused on one domain."""
    
    def __init__(self, name: str, expertise: str, system_prompt: str):
        self.name = name
        self.expertise = expertise
        self.system_prompt = system_prompt
    
    def respond(self, query: str) -> str:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.5,
            max_tokens=500
        )
        return response.choices[0].message.content

class RouterAgent:
    """Routes requests to the appropriate specialist."""
    
    def __init__(self):
        self.specialists: dict[str, SpecialistAgent] = {}
    
    def register(self, key: str, agent: SpecialistAgent):
        self.specialists[key] = agent
    
    def route(self, query: str) -> dict:
        """Determine which specialist should handle the query."""
        specialist_desc = "\n".join(
            f"- {key}: {agent.expertise}"
            for key, agent in self.specialists.items()
        )
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"""You are a routing agent. Given a user query, determine which specialist should handle it.

Available specialists:
{specialist_desc}

Respond in JSON: {{"specialist": "key", "reason": "why this specialist"}}
If no specialist fits, use "general"."""},
                {"role": "user", "content": query}
            ],
            response_format={"type": "json_object"},
            temperature=0
        )
        
        return json.loads(response.choices[0].message.content)
    
    def handle(self, query: str) -> dict:
        """Route and handle a query."""
        routing = self.route(query)
        specialist_key = routing.get("specialist", "general")
        
        print(f"  🔀 Routed to: {specialist_key} ({routing.get('reason', '')})")
        
        if specialist_key in self.specialists:
            agent = self.specialists[specialist_key]
            response = agent.respond(query)
        else:
            response = f"No specialist available for: {specialist_key}"
        
        return {
            "routing": routing,
            "specialist": specialist_key,
            "response": response
        }

# Build the team
router = RouterAgent()

router.register("devops", SpecialistAgent(
    name="DevOps Expert",
    expertise="Docker, Kubernetes, CI/CD, infrastructure, deployment, monitoring",
    system_prompt="You are a senior DevOps engineer. Give practical, concise answers with commands and examples."
))

router.register("security", SpecialistAgent(
    name="Security Analyst",
    expertise="Security vulnerabilities, access control, secrets, compliance, hardening",
    system_prompt="You are a cybersecurity expert. Focus on security best practices, threat analysis, and remediation."
))

router.register("coding", SpecialistAgent(
    name="Code Expert",
    expertise="Python, JavaScript, Go, code review, debugging, architecture",
    system_prompt="You are a senior software engineer. Provide clean, documented code examples."
))

# Test
queries = [
    "How do I set up horizontal pod autoscaling in Kubernetes?",
    "Review this Python code for security issues: api_key = 'sk-123'",
    "Write a function to parse JSON logs in Python",
]

for q in queries:
    print(f"\n❓ {q}")
    result = router.handle(q)
    print(f"💡 {result['response'][:200]}...")
    print("-" * 50)
```

---

## 4. Pipeline Agent System

```python
class PipelineAgent:
    """Runs a pipeline of agents sequentially."""
    
    def __init__(self, name: str):
        self.name = name
        self.stages: list[tuple[str, SpecialistAgent]] = []
    
    def add_stage(self, stage_name: str, agent: SpecialistAgent):
        self.stages.append((stage_name, agent))
    
    def run(self, initial_input: str) -> dict:
        """Run all stages sequentially, passing output to next stage."""
        results = {"input": initial_input, "stages": []}
        current_input = initial_input
        
        for stage_name, agent in self.stages:
            print(f"  📌 Stage: {stage_name}...")
            output = agent.respond(current_input)
            
            results["stages"].append({
                "stage": stage_name,
                "agent": agent.name,
                "output": output
            })
            
            # Next stage gets: original input + all previous outputs
            current_input = f"Original request: {initial_input}\n\nPrevious stage ({stage_name}) output:\n{output}\n\nContinue with your role."
        
        results["final_output"] = results["stages"][-1]["output"]
        return results

# Build the pipeline
pipeline = PipelineAgent("Incident Response Pipeline")

pipeline.add_stage("analyze", SpecialistAgent(
    "Analyzer", "Error analysis",
    "You are an incident analyzer. Given an error or incident, identify the root cause and severity. Be concise."
))

pipeline.add_stage("plan", SpecialistAgent(
    "Planner", "Action planning",
    "You are an incident planner. Given an analysis, create a numbered remediation plan. Be specific."
))

pipeline.add_stage("implement", SpecialistAgent(
    "Implementer", "Code and commands",
    "You are a DevOps implementer. Given a plan, provide the exact commands and code to execute. Include verification steps."
))

# Run the pipeline
result = pipeline.run(
    "Production API is returning 503 errors. Load balancer health checks are failing for 2 of 3 backend pods."
)

for stage in result["stages"]:
    print(f"\n=== {stage['stage'].upper()} ({stage['agent']}) ===")
    print(stage["output"][:300])
```

---

## 5. Supervisor Agent

```python
class SupervisorAgent:
    """Orchestrates workers and combines their outputs."""
    
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self.workers: dict[str, SpecialistAgent] = {}
    
    def add_worker(self, key: str, agent: SpecialistAgent):
        self.workers[key] = agent
    
    def delegate(self, task: str, worker_keys: list[str] | None = None) -> dict:
        """Assign task to specific workers or auto-select."""
        keys = worker_keys or list(self.workers.keys())
        
        results = {}
        for key in keys:
            if key in self.workers:
                print(f"  👷 {key} working...")
                results[key] = self.workers[key].respond(task)
        
        return results
    
    def synthesize(self, task: str, worker_results: dict) -> str:
        """Combine worker outputs into a final answer."""
        results_text = "\n\n".join(
            f"=== {key} ===\n{output}"
            for key, output in worker_results.items()
        )
        
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": """You are a supervisor agent. 
Multiple specialist workers have provided their analysis. 
Synthesize their outputs into a comprehensive, unified response.
Resolve any contradictions. Highlight consensus and disagreements."""},
                {"role": "user", "content": f"""Task: {task}

Worker Outputs:
{results_text}

Provide a synthesized response:"""}
            ],
            temperature=0.3
        )
        
        return response.choices[0].message.content
    
    def handle(self, task: str) -> str:
        """Full supervisor workflow: delegate → synthesize."""
        worker_results = self.delegate(task)
        final = self.synthesize(task, worker_results)
        return final

# Build supervisor team
supervisor = SupervisorAgent()

supervisor.add_worker("architect", SpecialistAgent(
    "Cloud Architect", "Architecture design",
    "You are a cloud architect. Focus on scalability, reliability, and cost."
))

supervisor.add_worker("security", SpecialistAgent(
    "Security Expert", "Security analysis",
    "You are a security expert. Focus on vulnerabilities, compliance, and hardening."
))

supervisor.add_worker("operations", SpecialistAgent(
    "SRE", "Operations and reliability",
    "You are an SRE. Focus on monitoring, incident response, and SLOs."
))

# Run
task = "Design a deployment strategy for a new payment processing microservice"
result = supervisor.handle(task)
print(f"\n=== FINAL RECOMMENDATION ===\n{result}")
```

---

## 6. Exercises

### Exercise 1: Debate Agents
```python
# Build two agents that debate a topic:
# 1. Agent A proposes a solution
# 2. Agent B critiques it
# 3. Agent A refines based on critique
# 4. A judge agent picks the best approach
# Topic: "Monolith vs Microservices for a startup"
```

### Exercise 2: Research Team
```python
# Build a multi-agent research team:
# 1. Researcher agent: gathers information (simulated)
# 2. Analyst agent: analyzes the research
# 3. Writer agent: produces a summary report
# 4. Editor agent: reviews and improves the report
# Topic: "Best practices for Kubernetes security in 2024"
```

### Exercise 3: Self-Improving Agent
```python
# Build an agent that:
# 1. Generates an initial response to a coding question
# 2. A reviewer agent checks for errors and improvements
# 3. The original agent incorporates feedback
# 4. Compare quality of v1 vs v2
# Run 3 rounds and track improvement
```

---

## Solutions

See [solutions/day27_solutions.py](../solutions/day27_solutions.py)

---

## Key Takeaways
- Multi-agent systems split complexity across specialized agents
- Router pattern: classify and dispatch to the right expert
- Pipeline pattern: sequential processing (analyze → plan → implement)
- Supervisor pattern: parallel work + synthesized results
- Each agent should have a focused, clear system prompt
- Multi-agent adds latency and cost — use when complexity justifies it

**Tomorrow:** Agent evaluation, logging & guardrails →
