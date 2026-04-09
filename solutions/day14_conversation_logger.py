# ============================================
# Day 14 Solution — Conversation Logger with OOP
# ============================================

import json
from datetime import datetime
from pathlib import Path


class Message:
    """A single message in a conversation."""

    def __init__(self, role: str, content: str, timestamp: str | None = None):
        self.role = role
        self.content = content
        self.timestamp = timestamp or datetime.now().isoformat()
        self.token_estimate = max(1, len(content) // 4)

    def to_dict(self) -> dict:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp,
            "token_estimate": self.token_estimate,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Message":
        msg = cls(data["role"], data["content"], data.get("timestamp"))
        msg.token_estimate = data.get("token_estimate", len(data["content"]) // 4)
        return msg

    def __str__(self):
        return f"[{self.role.upper()}] {self.content[:60]}"


class Conversation:
    """A conversation consisting of multiple messages."""

    def __init__(self, title: str, conv_id: str | None = None):
        self.id = conv_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.title = title
        self.messages: list[Message] = []
        self.created_at = datetime.now().isoformat()

    def add_message(self, role: str, content: str) -> Message:
        msg = Message(role, content)
        self.messages.append(msg)
        return msg

    def get_messages(self, last_n: int | None = None) -> list[Message]:
        if last_n:
            return self.messages[-last_n:]
        return self.messages

    def search(self, keyword: str) -> list[Message]:
        keyword_lower = keyword.lower()
        return [m for m in self.messages if keyword_lower in m.content.lower()]

    def token_count(self) -> int:
        return sum(m.token_estimate for m in self.messages)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "created_at": self.created_at,
            "message_count": len(self.messages),
            "total_tokens": self.token_count(),
            "messages": [m.to_dict() for m in self.messages],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Conversation":
        conv = cls(data["title"], data["id"])
        conv.created_at = data.get("created_at", conv.created_at)
        conv.messages = [Message.from_dict(m) for m in data.get("messages", [])]
        return conv

    def export_markdown(self, filepath: str):
        lines = [f"# {self.title}", f"*Created: {self.created_at}*\n"]
        for msg in self.messages:
            prefix = "**User:**" if msg.role == "user" else "**Assistant:**"
            lines.append(f"{prefix} {msg.content}\n")
        Path(filepath).write_text("\n".join(lines))

    def __str__(self):
        return f"Conversation('{self.title}', {len(self.messages)} messages)"


class ConversationStore:
    """Manages multiple conversations with disk persistence."""

    def __init__(self, storage_dir: str = "conversations"):
        self.storage_path = Path(storage_dir)
        self.storage_path.mkdir(exist_ok=True)
        self.conversations: dict[str, Conversation] = {}
        self.load_from_disk()

    def create(self, title: str) -> Conversation:
        conv = Conversation(title)
        self.conversations[conv.id] = conv
        return conv

    def get(self, conv_id: str) -> Conversation | None:
        return self.conversations.get(conv_id)

    def list_all(self) -> list[dict]:
        return [
            {"id": c.id, "title": c.title, "messages": len(c.messages), "tokens": c.token_count()}
            for c in self.conversations.values()
        ]

    def search_all(self, keyword: str) -> list[dict]:
        results = []
        for conv in self.conversations.values():
            matches = conv.search(keyword)
            for msg in matches:
                results.append({
                    "conversation": conv.title,
                    "role": msg.role,
                    "content": msg.content[:80],
                })
        return results

    def save_to_disk(self):
        for conv_id, conv in self.conversations.items():
            filepath = self.storage_path / f"{conv_id}.json"
            with open(filepath, "w") as f:
                json.dump(conv.to_dict(), f, indent=2)

    def load_from_disk(self):
        for filepath in self.storage_path.glob("*.json"):
            try:
                with open(filepath) as f:
                    data = json.load(f)
                conv = Conversation.from_dict(data)
                self.conversations[conv.id] = conv
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Warning: Could not load {filepath}: {e}")

    def get_stats(self) -> dict:
        total_msgs = sum(len(c.messages) for c in self.conversations.values())
        total_tokens = sum(c.token_count() for c in self.conversations.values())
        return {
            "total_conversations": len(self.conversations),
            "total_messages": total_msgs,
            "total_tokens": total_tokens,
        }


class AgentSimulator:
    """Simple keyword-based response simulator."""

    RESPONSES = {
        "docker": "Docker lets you containerize applications. Use `docker build` to create images.",
        "kubernetes": "Kubernetes orchestrates containers. Key objects: Pod, Service, Deployment.",
        "python": "Python is great for DevOps and AI. Key libraries: requests, boto3, langchain.",
        "cicd": "CI/CD automates build, test, and deploy. Popular tools: GitHub Actions, Jenkins.",
        "help": "I can help with Docker, Kubernetes, Python, CI/CD, and more!",
    }

    def respond(self, message: str) -> str:
        msg_lower = message.lower()
        for keyword, response in self.RESPONSES.items():
            if keyword in msg_lower:
                return response
        return "I'm not sure about that. Try asking about Docker, Kubernetes, or Python!"


def main():
    """Interactive conversation logger application."""
    store = ConversationStore()
    agent = AgentSimulator()
    current_conv: Conversation | None = None

    print("=== Conversation Logger ===")
    print("Type /help for commands\n")

    while True:
        prompt = f"[{current_conv.title}] " if current_conv else "[no conversation] "
        user_input = input(f"{prompt}You: ").strip()

        if not user_input:
            continue

        if user_input.startswith("/"):
            parts = user_input.split(maxsplit=1)
            command = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else ""

            if command == "/quit":
                store.save_to_disk()
                stats = store.get_stats()
                print(f"\nSaved. Stats: {stats}")
                print("Goodbye!")
                break

            elif command == "/new":
                title = arg or f"Conversation {len(store.conversations) + 1}"
                current_conv = store.create(title)
                print(f"Created: {current_conv}")

            elif command == "/list":
                convos = store.list_all()
                if convos:
                    for c in convos:
                        marker = " ←" if current_conv and c["id"] == current_conv.id else ""
                        print(f"  {c['id']}: {c['title']} ({c['messages']} msgs){marker}")
                else:
                    print("  No conversations. Use /new to create one.")

            elif command == "/switch":
                conv = store.get(arg)
                if conv:
                    current_conv = conv
                    print(f"Switched to: {conv}")
                else:
                    print(f"Conversation '{arg}' not found. Use /list to see IDs.")

            elif command == "/history":
                if current_conv:
                    for msg in current_conv.messages:
                        print(f"  {msg}")
                else:
                    print("  No active conversation.")

            elif command == "/search":
                results = store.search_all(arg)
                if results:
                    for r in results:
                        print(f"  [{r['conversation']}] {r['role']}: {r['content']}")
                else:
                    print(f"  No results for '{arg}'")

            elif command == "/stats":
                print(f"  Store: {store.get_stats()}")
                if current_conv:
                    print(f"  Current: {len(current_conv.messages)} msgs, {current_conv.token_count()} tokens")

            elif command == "/export":
                if current_conv:
                    filepath = arg or f"{current_conv.id}.md"
                    current_conv.export_markdown(filepath)
                    print(f"  Exported to {filepath}")
                else:
                    print("  No active conversation.")

            elif command == "/save":
                store.save_to_disk()
                print("  Saved all conversations.")

            elif command == "/help":
                print("""  Commands:
    /new [title]    — Start a new conversation
    /list           — List all conversations
    /switch [id]    — Switch conversation
    /history        — Show current conversation
    /search [word]  — Search across all conversations
    /stats          — Show statistics
    /export [path]  — Export to Markdown
    /save           — Save all to disk
    /quit           — Save and exit""")
            else:
                print(f"  Unknown command: {command}")
            continue

        # Regular message
        if not current_conv:
            current_conv = store.create("Default")
            print(f"  (Auto-created conversation: {current_conv.title})")

        current_conv.add_message("user", user_input)
        response = agent.respond(user_input)
        current_conv.add_message("assistant", response)
        print(f"  Bot: {response}\n")


if __name__ == "__main__":
    main()
