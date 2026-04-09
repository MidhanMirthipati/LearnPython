# ============================================
# Capstone Project — DevOps Assistant Agent
# Logger Module
# ============================================

import json
from datetime import datetime
from pathlib import Path


class AgentLogger:
    """Structured logging for the agent system."""

    def __init__(self, log_dir: str = "logs", level: str = "INFO"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.level = level
        self.levels = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3}
        self.entries: list[dict] = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    def _should_log(self, level: str) -> bool:
        return self.levels.get(level, 0) >= self.levels.get(self.level, 0)

    def _log(self, level: str, component: str, message: str, data: dict | None = None):
        if not self._should_log(level):
            return

        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "component": component,
            "message": message,
        }
        if data:
            entry["data"] = data

        self.entries.append(entry)

        # Print to console
        emoji = {"DEBUG": "🔍", "INFO": "ℹ️", "WARNING": "⚠️", "ERROR": "❌"}.get(level, "")
        print(f"  {emoji} [{level}] {component}: {message}")

    def debug(self, component: str, message: str, **data):
        self._log("DEBUG", component, message, data if data else None)

    def info(self, component: str, message: str, **data):
        self._log("INFO", component, message, data if data else None)

    def warning(self, component: str, message: str, **data):
        self._log("WARNING", component, message, data if data else None)

    def error(self, component: str, message: str, **data):
        self._log("ERROR", component, message, data if data else None)

    def log_tool_call(self, tool_name: str, args: dict, result: str):
        self._log("INFO", "tools", f"Called {tool_name}", {"args": args, "result_len": len(result)})

    def log_llm_call(self, model: str, tokens: int, latency_ms: int):
        self._log("INFO", "llm", f"API call to {model}", {"tokens": tokens, "latency_ms": latency_ms})

    def save_session(self):
        """Save session log to disk."""
        filepath = self.log_dir / f"session_{self.session_id}.json"
        with open(filepath, "w") as f:
            json.dump({
                "session_id": self.session_id,
                "entries": self.entries,
                "total_entries": len(self.entries),
            }, f, indent=2)
        return str(filepath)

    def get_summary(self) -> dict:
        level_counts = {}
        for entry in self.entries:
            level = entry["level"]
            level_counts[level] = level_counts.get(level, 0) + 1
        return {
            "session_id": self.session_id,
            "total_entries": len(self.entries),
            "by_level": level_counts,
        }
