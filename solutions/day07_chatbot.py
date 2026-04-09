# ============================================
# Day 7 Solution — CLI Chatbot Skeleton
# ============================================

from datetime import datetime

# --- Configuration ---
BOT_CONFIG = {
    "name": "PyBot",
    "version": "1.0",
    "personality": "helpful",
}

# --- Knowledge Base ---
RESPONSES = {
    "hello": "Hello! How can I help you today?",
    "hi": "Hi there! What can I do for you?",
    "python": "Python is a versatile programming language, great for AI, automation, and web development!",
    "docker": "Docker is a containerization platform. Use `docker run` to start containers and `docker build` to create images.",
    "kubernetes": "Kubernetes (K8s) orchestrates containers at scale. Key concepts: Pods, Services, Deployments.",
    "cicd": "CI/CD stands for Continuous Integration / Continuous Delivery. Tools: GitHub Actions, Jenkins, GitLab CI.",
    "devops": "DevOps is a culture and practice that bridges development and operations for faster, more reliable delivery.",
    "ai": "AI (Artificial Intelligence) enables machines to learn and make decisions. Popular tools: TensorFlow, PyTorch, LangChain.",
    "agent": "AI Agents are LLMs with tools and loops. They can take autonomous actions to complete tasks.",
    "help": "I can answer questions about Python, Docker, Kubernetes, CI/CD, DevOps, and AI!",
    "bye": "Goodbye! Happy coding! 👋",
}


def estimate_tokens(text: str) -> int:
    """Estimate token count (~4 chars per token)."""
    return max(1, len(text) // 4)


def find_response(message: str) -> str:
    """Find a response based on keyword matching."""
    msg_lower = message.lower()
    for keyword, response in RESPONSES.items():
        if keyword in msg_lower:
            return response
    return "I'm not sure about that. Try asking about Python, Docker, Kubernetes, DevOps, or AI!"


def add_to_history(role: str, content: str, history: list):
    """Add a message to conversation history."""
    history.append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "tokens": estimate_tokens(content),
    })


def display_history(history: list):
    """Display conversation history."""
    if not history:
        print("  No conversation history yet.")
        return
    print(f"\n  --- Conversation History ({len(history)} messages) ---")
    for msg in history:
        role = msg["role"].upper()
        time = msg["timestamp"]
        content = msg["content"][:60]
        print(f"  [{time}] {role}: {content}")
    print()


def get_session_stats(history: list) -> dict:
    """Calculate session statistics."""
    user_msgs = [m for m in history if m["role"] == "user"]
    bot_msgs = [m for m in history if m["role"] == "assistant"]
    total_tokens = sum(m["tokens"] for m in history)
    return {
        "total_messages": len(history),
        "user_messages": len(user_msgs),
        "bot_messages": len(bot_msgs),
        "total_tokens": total_tokens,
        "estimated_cost": f"${total_tokens * 0.00003:.4f}",
    }


def show_help():
    """Display available commands."""
    print("""
  Available Commands:
    /help     — Show this help message
    /history  — Show conversation history
    /tools    — Show available topics
    /stats    — Show session statistics
    /quit     — Exit the chatbot
    """)


def show_tools():
    """Display available topics."""
    topics = list(RESPONSES.keys())
    print(f"  I know about: {', '.join(topics)}")


def main():
    """Main chatbot loop."""
    history = []

    print(f"\n{'='*50}")
    print(f"  Welcome to {BOT_CONFIG['name']} v{BOT_CONFIG['version']}!")
    print(f"{'='*50}")

    name = input("  What's your name? ").strip() or "User"
    print(f"\n  Hello, {name}! Type /help for commands or just start chatting.\n")

    while True:
        user_input = input(f"  {name}: ").strip()

        if not user_input:
            continue

        # Handle commands
        if user_input.startswith("/"):
            command = user_input.lower()

            if command == "/quit":
                stats = get_session_stats(history)
                print(f"\n  --- Session Summary ---")
                for key, value in stats.items():
                    print(f"  {key}: {value}")
                print(f"\n  Goodbye, {name}! 👋\n")
                break

            elif command == "/help":
                show_help()

            elif command == "/history":
                display_history(history)

            elif command == "/tools":
                show_tools()

            elif command == "/stats":
                stats = get_session_stats(history)
                for key, value in stats.items():
                    print(f"  {key}: {value}")

            else:
                print(f"  Unknown command: {command}. Type /help for options.")

            continue

        # Handle regular messages
        add_to_history("user", user_input, history)

        response = find_response(user_input)
        add_to_history("assistant", response, history)

        print(f"  {BOT_CONFIG['name']}: {response}\n")


if __name__ == "__main__":
    main()
