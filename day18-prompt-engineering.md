# Day 18: Prompt Engineering in Code

## Learning Goals
- Design effective system and user prompts
- Use structured output (JSON mode)
- Build prompt templates and chains
- Implement few-shot prompting programmatically

---

## 1. System Prompts — Setting the Agent's Behavior

```python
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

# A well-structured system prompt
SYSTEM_PROMPT = """You are a senior DevOps engineer with 10 years of experience.

Your expertise:
- Docker, Kubernetes, Terraform
- CI/CD (GitHub Actions, Jenkins, GitLab CI)
- AWS, Azure, GCP
- Python scripting for automation

Communication style:
- Be concise and practical
- Always provide code examples when relevant
- Mention potential pitfalls and best practices
- If asked about something outside DevOps, redirect politely

Output format:
- Use headers and bullet points
- Include command examples in code blocks
- End with a "Next Steps" section when appropriate"""

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "How do I set up a multi-stage Docker build?"}
    ]
)
print(response.choices[0].message.content)
```

---

## 2. Prompt Templates

```python
class PromptTemplate:
    """Reusable prompt template with variable substitution."""
    
    def __init__(self, template: str):
        self.template = template
    
    def render(self, **kwargs) -> str:
        """Fill in template variables."""
        result = self.template
        for key, value in kwargs.items():
            result = result.replace(f"{{{key}}}", str(value))
        return result

# Define reusable templates
EXPLAIN_TEMPLATE = PromptTemplate("""
Explain {topic} for someone who is a {level} in DevOps.
Focus on: {focus_areas}
Keep your response under {max_words} words.
Include a practical example.
""")

CODE_REVIEW_TEMPLATE = PromptTemplate("""
Review the following {language} code for:
1. Bugs and errors
2. Security vulnerabilities
3. Performance issues
4. Best practice violations

Code:
```{language}
{code}
```

Provide your review as a numbered list of findings with severity (HIGH/MEDIUM/LOW).
""")

TROUBLESHOOT_TEMPLATE = PromptTemplate("""
I'm experiencing this error in my {environment} environment:

Error message: {error}
Context: {context}

Please:
1. Explain what this error means
2. List the most common causes
3. Provide step-by-step fix instructions
4. Suggest how to prevent it in the future
""")

# Using templates
prompt = EXPLAIN_TEMPLATE.render(
    topic="Kubernetes Ingress controllers",
    level="beginner",
    focus_areas="when to use them, basic configuration, common providers",
    max_words=300
)
print(prompt)

review_prompt = CODE_REVIEW_TEMPLATE.render(
    language="python",
    code="""
import os
api_key = "sk-abc123"
password = input("Enter password: ")
data = eval(input("Enter expression: "))
"""
)
print(review_prompt)
```

---

## 3. Structured Output (JSON Mode)

All three providers support JSON output, but the mechanism varies:

### OpenAI (native JSON mode)
```python
from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()
client = OpenAI()

def analyze_error_openai(error_message: str) -> dict:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": """You are an error analysis expert.
Always respond in this exact JSON format:
{
    "error_type": "the category of error",
    "severity": "low|medium|high|critical",
    "root_cause": "likely root cause",
    "fix_steps": ["step 1", "step 2"],
    "prevention": "how to prevent this"
}"""},
            {"role": "user", "content": f"Analyze this error: {error_message}"}
        ],
        response_format={"type": "json_object"},  # OpenAI-specific
        temperature=0.3
    )
    return json.loads(response.choices[0].message.content)
```

### Anthropic (prompt-based JSON)
```python
import anthropic
import json

client = anthropic.Anthropic()

def analyze_error_anthropic(error_message: str) -> dict:
    response = client.messages.create(
        model="claude-sonnet-4-20250514", max_tokens=500,
        system="""You are an error analysis expert. Always respond with ONLY valid JSON:
{"error_type": "...", "severity": "...", "root_cause": "...", "fix_steps": [...], "prevention": "..."}""",
        messages=[{"role": "user", "content": f"Analyze this error: {error_message}"}],
        temperature=0.3
    )
    return json.loads(response.content[0].text)
```

### Gemini (native JSON mode)
```python
import google.generativeai as genai
import json

genai.configure()
model = genai.GenerativeModel("gemini-2.0-flash")

def analyze_error_gemini(error_message: str) -> dict:
    response = model.generate_content(
        f"""You are an error analysis expert. Analyze this error and respond in JSON:
{error_message}

Format: {{"error_type": "...", "severity": "...", "root_cause": "...", "fix_steps": [...], "prevention": "..."}}""",
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",  # Gemini-specific
            temperature=0.3
        )
    )
    return json.loads(response.text)
```

---

## 4. Few-Shot Prompting

```python
def classify_devops_task(task_description: str) -> str:
    """Classify a DevOps task using few-shot examples."""
    
    messages = [
        {"role": "system", "content": "Classify DevOps tasks into categories. Respond with ONLY the category name."},
        
        # Few-shot examples
        {"role": "user", "content": "Set up a new Jenkins pipeline for the frontend app"},
        {"role": "assistant", "content": "CI/CD"},
        
        {"role": "user", "content": "The production database is running out of disk space"},
        {"role": "assistant", "content": "INFRASTRUCTURE"},
        
        {"role": "user", "content": "Create a Dockerfile for the Python microservice"},
        {"role": "assistant", "content": "CONTAINERIZATION"},
        
        {"role": "user", "content": "Investigate why response times increased after deployment"},
        {"role": "assistant", "content": "MONITORING"},
        
        {"role": "user", "content": "Write a Terraform module for the new VPC"},
        {"role": "assistant", "content": "INFRASTRUCTURE_AS_CODE"},
        
        {"role": "user", "content": "Someone pushed credentials to the public repo"},
        {"role": "assistant", "content": "SECURITY"},
        
        # Actual task to classify
        {"role": "user", "content": task_description}
    ]
    
    # Works with any provider — using OpenAI here (swap as needed)
    from openai import OpenAI
    client = OpenAI()
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0,
        max_tokens=20
    )
    
    return response.choices[0].message.content.strip()

# Test
tasks = [
    "Set up Prometheus monitoring for the K8s cluster",
    "Create a GitHub Actions workflow for automated testing",
    "Rotate all API keys across production services",
    "Debug the failing Docker build for the auth service",
]

for task in tasks:
    category = classify_devops_task(task)
    print(f"  {category:<25} ← {task}")
```

---

## 5. Chain of Thought Prompting

```python
def solve_with_reasoning(problem: str) -> dict:
    """Use chain-of-thought to solve a problem step by step."""
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": """You are a DevOps problem solver.
When given a problem:
1. First, analyze what's happening (ANALYSIS)
2. List possible causes (CAUSES)
3. Determine the most likely cause (DIAGNOSIS)
4. Provide the solution (SOLUTION)

Respond in JSON format:
{
    "analysis": "what the problem looks like",
    "causes": ["cause1", "cause2", "cause3"],
    "diagnosis": "most likely cause and why",
    "solution": "step by step solution",
    "commands": ["command1", "command2"]
}"""},
            {"role": "user", "content": problem}
        ],
        response_format={"type": "json_object"},
        temperature=0.3
    )
    
    return json.loads(response.choices[0].message.content)
```

---

## 6. Prompt Chaining

```python
def research_and_implement(topic: str) -> dict:
    """Chain multiple prompts: research → plan → implement."""
    
    # Step 1: Research
    # Note: You can use different providers for different steps!
    research = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a technical researcher. Summarize the key concepts concisely."},
            {"role": "user", "content": f"Summarize the key concepts of: {topic}"}
        ],
        max_tokens=300
    ).choices[0].message.content
    
    # Step 2: Plan (uses research output)
    plan = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a project planner. Create an implementation plan."},
            {"role": "user", "content": f"Based on this research:\n{research}\n\nCreate a step-by-step implementation plan."}
        ],
        max_tokens=400
    ).choices[0].message.content
    
    # Step 3: Implement (uses plan)
    code = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a Python developer. Write clean, working code."},
            {"role": "user", "content": f"Implement this plan in Python:\n{plan}"}
        ],
        max_tokens=800
    ).choices[0].message.content
    
    return {
        "research": research,
        "plan": plan,
        "code": code
    }
```

---

## 7. Exercises

### Exercise 1: Prompt Template Library
```python
# Build a library of at least 5 prompt templates for DevOps:
# 1. Incident response template
# 2. Architecture review template
# 3. Migration planning template
# 4. Documentation generator template
# 5. Runbook creator template
# Each should use PromptTemplate with proper variables
# Test each with realistic inputs
```

### Exercise 2: Structured Extractor
```python
# Build a function that takes raw text (like an email or Slack message)
# and extracts structured information:
# - What is the issue?
# - What is the severity?
# - Which service is affected?
# - Is there a deadline?
# Return as a validated JSON object
```

### Exercise 3: Few-Shot Classifier
```python
# Build a classifier that categorizes user messages for an AI agent:
# Categories: "question", "command", "feedback", "complaint", "small_talk"
# 1. Define 3 few-shot examples per category
# 2. Test with 10 new messages
# 3. Track accuracy (manually judge the results)
# 4. Try adjusting temperature (0 vs 0.5 vs 1.0) and compare
```

---

## Solutions

See [solutions/day18_solutions.py](../solutions/day18_solutions.py)

---

## Key Takeaways
- System prompts set behavior, expertise, and output format
- Prompt templates make prompts reusable and consistent
- JSON mode: OpenAI uses `response_format`, Gemini uses `response_mime_type`, Anthropic relies on prompt instructions
- Few-shot examples teach the model patterns by example
- Chain-of-thought prompting improves reasoning quality
- All prompt techniques work across OpenAI, Anthropic, and Gemini — adapt the API call syntax
- Prompt chaining: pipe the output of one call into the next

**Tomorrow:** Working with data using Pandas →
