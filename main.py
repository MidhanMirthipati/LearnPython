# ============================================
# Capstone Project — DevOps Assistant Agent
# Main Application Entry Point
# ============================================
"""
DevOps Assistant Agent — Capstone Project
==========================================
A conversational AI agent for DevOps tasks with:
- Tool integration (server checks, Docker, K8s, CI/CD, logs, costs)
- Conversation memory with token budget management
- Input/output guardrails for safety
- Structured logging

Usage:
    python -m solutions.day29_capstone.main

Or if running directly:
    cd solutions/day29_capstone
    python main.py
"""

import sys
import os

# Add parent directory to path for direct execution
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from day29_capstone import config
    from day29_capstone.agents import DevOpsAgent
else:
    from . import config
    from .agents import DevOpsAgent


def main():
    """Main application loop."""
    # Display config
    config.display_config()

    # Initialize agent
    agent = DevOpsAgent()

    print("=" * 50)
    print(f"  Welcome to {config.APP_NAME}!")
    print("=" * 50)
    print("  Type /help for commands, or just start chatting.")
    print("  Ask about servers, Docker, K8s, CI/CD, logs, costs.")
    print()

    while True:
        try:
            user_input = input("  You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n  Goodbye!")
            break

        if not user_input:
            continue

        # Handle commands
        if user_input.startswith("/"):
            result = agent.handle_command(user_input)
            if result == "QUIT":
                # Save and show summary
                log_path = agent.logger.save_session()
                stats = agent.handle_command("/stats")
                print(f"\n{stats}")
                print(f"  Log saved: {log_path}")
                print("\n  Goodbye! Happy DevOps-ing! 👋\n")
                break
            elif result:
                print(f"\n{result}\n")
            else:
                print(f"  Unknown command. Type /help for options.\n")
            continue

        # Regular chat
        response = agent.chat(user_input)
        print(f"\n  Agent: {response}\n")


if __name__ == "__main__":
    main()
