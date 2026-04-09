# 30-Day Python for AI Agents — From Zero to Intermediate

## Course Overview

A structured 30-day course designed for someone with no programming background, progressing from Python basics to building functional AI agents. Each day is ~1.5–2 hours of study + practice.

---

## Course Structure

### Week 1: Python Foundations (Days 1–7)
| Day | Topic | File |
|-----|-------|------|
| 1 | [Setup, Variables & Data Types](week1/day01-setup-variables.md) | `week1/day01-setup-variables.md` |
| 2 | [Strings, Input & Output](week1/day02-strings-io.md) | `week1/day02-strings-io.md` |
| 3 | [Conditionals & Boolean Logic](week1/day03-conditionals.md) | `week1/day03-conditionals.md` |
| 4 | [Loops & Iteration](week1/day04-loops.md) | `week1/day04-loops.md` |
| 5 | [Functions & Scope](week1/day05-functions.md) | `week1/day05-functions.md` |
| 6 | [Lists, Tuples & Dictionaries](week1/day06-data-structures.md) | `week1/day06-data-structures.md` |
| 7 | [**Mini-Project:** CLI Chatbot Skeleton](week1/day07-project-cli-chatbot.md) | `week1/day07-project-cli-chatbot.md` |

### Week 2: Intermediate Python (Days 8–14)
| Day | Topic | File |
|-----|-------|------|
| 8 | [File I/O & JSON](week2/day08-files-json.md) | `week2/day08-files-json.md` |
| 9 | [Error Handling & Debugging](week2/day09-error-handling.md) | `week2/day09-error-handling.md` |
| 10 | [Modules, Packages & pip](week2/day10-modules-pip.md) | `week2/day10-modules-pip.md` |
| 11 | [Object-Oriented Programming — Basics](week2/day11-oop-basics.md) | `week2/day11-oop-basics.md` |
| 12 | [OOP — Inheritance & Composition](week2/day12-oop-inheritance.md) | `week2/day12-oop-inheritance.md` |
| 13 | [List Comprehensions, Generators & Lambdas](week2/day13-comprehensions-generators.md) | `week2/day13-comprehensions-generators.md` |
| 14 | [**Mini-Project:** Conversation Logger with OOP](week2/day14-project-conversation-logger.md) | `week2/day14-project-conversation-logger.md` |

### Week 3: APIs, Data & AI Foundations (Days 15–21)
| Day | Topic | File |
|-----|-------|------|
| 15 | [HTTP Requests & REST APIs](week3/day15-http-apis.md) | `week3/day15-http-apis.md` |
| 16 | [Environment Variables & Secrets Management](week3/day16-env-secrets.md) | `week3/day16-env-secrets.md` |
| 17 | [Calling the OpenAI API](week3/day17-openai-api.md) | `week3/day17-openai-api.md` |
| 18 | [Prompt Engineering in Code](week3/day18-prompt-engineering.md) | `week3/day18-prompt-engineering.md` |
| 19 | [Working with Data: Pandas Basics](week3/day19-pandas-basics.md) | `week3/day19-pandas-basics.md` |
| 20 | [Async Python & Concurrency](week3/day20-async-python.md) | `week3/day20-async-python.md` |
| 21 | [**Mini-Project:** AI-Powered Q&A Bot](week3/day21-project-qa-bot.md) | `week3/day21-project-qa-bot.md` |

### Week 4: AI Agents Deep Dive (Days 22–28)
| Day | Topic | File |
|-----|-------|------|
| 22 | [What Are AI Agents — Architecture & Concepts](week4/day22-agent-concepts.md) | `week4/day22-agent-concepts.md` |
| 23 | [Tool Use — Giving Agents Capabilities](week4/day23-tool-use.md) | `week4/day23-tool-use.md` |
| 24 | [Memory & State Management for Agents](week4/day24-agent-memory.md) | `week4/day24-agent-memory.md` |
| 25 | [Building Agents with LangChain](week4/day25-langchain-agents.md) | `week4/day25-langchain-agents.md` |
| 26 | [RAG — Retrieval Augmented Generation](week4/day26-rag.md) | `week4/day26-rag.md` |
| 27 | [Multi-Agent Systems](week4/day27-multi-agent.md) | `week4/day27-multi-agent.md` |
| 28 | [Agent Evaluation, Logging & Guardrails](week4/day28-eval-guardrails.md) | `week4/day28-eval-guardrails.md` |

### Capstone (Days 29–30)
| Day | Topic | File |
|-----|-------|------|
| 29 | [**Capstone Project:** DevOps Assistant Agent — Part 1](capstone/day29-capstone-part1.md) | `capstone/day29-capstone-part1.md` |
| 30 | [**Capstone Project:** DevOps Assistant Agent — Part 2](capstone/day30-capstone-part2.md) | `capstone/day30-capstone-part2.md` |

### Project Solutions
All complete, runnable code solutions are in the [`solutions/`](solutions/) directory.

---

## Prerequisites

- A computer with internet access
- Python 3.10+ installed
- A code editor (VS Code recommended)
- An OpenAI API key (from Day 17 onward) — a free-tier or $5 credit is sufficient

## How to Use This Course

1. **Read the day's markdown file** — it contains theory, examples, and exercises
2. **Type out every code example** — do not copy-paste; typing builds muscle memory
3. **Complete all exercises** — check your work against `solutions/`
4. **Mini-projects (Days 7, 14, 21)** — build from scratch, then compare
5. **Capstone (Days 29–30)** — bring everything together

## Setup Instructions

```bash
# Install Python 3.10+
# Windows: Download from https://www.python.org/downloads/
# Make sure to check "Add Python to PATH" during installation

# Verify installation
python --version

# Create course virtual environment
python -m venv ai-course-env

# Activate it
# Windows:
ai-course-env\Scripts\activate
# Linux/Mac:
source ai-course-env/bin/activate

# Install core packages (needed from Week 3 onward)
pip install openai requests python-dotenv pandas langchain chromadb
```
