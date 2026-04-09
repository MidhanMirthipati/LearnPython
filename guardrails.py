# ============================================
# Capstone Project — DevOps Assistant Agent
# Guardrails Module
# ============================================

import re
from datetime import datetime


class InputGuardrail:
    """Validates and sanitizes user input before processing."""

    def __init__(self, max_length: int = 2000, blocked_patterns: list[str] | None = None):
        self.max_length = max_length
        self.blocked_patterns = blocked_patterns or []
        self.block_log: list[dict] = []

    def validate(self, user_input: str) -> dict:
        """Validate user input. Returns dict with 'safe' bool and any 'issues'."""
        issues = []

        # Length check
        if len(user_input) > self.max_length:
            issues.append(f"Input too long ({len(user_input)}/{self.max_length})")

        # Empty check
        if not user_input.strip():
            issues.append("Empty input")

        # Injection pattern check
        input_lower = user_input.lower()
        for pattern in self.blocked_patterns:
            if re.search(pattern, input_lower):
                issues.append(f"Blocked pattern detected")
                self.block_log.append({
                    "input_preview": user_input[:50],
                    "pattern": pattern[:30],
                    "timestamp": datetime.now().isoformat(),
                })
                break  # One block is enough

        return {
            "safe": len(issues) == 0,
            "issues": issues,
            "sanitized_input": user_input[:self.max_length].strip(),
        }


class OutputGuardrail:
    """Validates LLM output before returning to user."""

    def __init__(self, max_length: int = 5000):
        self.max_length = max_length

    def validate(self, output: str) -> dict:
        """Validate output. Returns dict with 'safe' bool and cleaned 'output'."""
        issues = []

        # Length check
        if len(output) > self.max_length:
            output = output[:self.max_length] + "\n\n[Output truncated]"
            issues.append("Output truncated to length limit")

        # PII check
        if re.search(r'\b\d{3}[-.]?\d{2}[-.]?\d{4}\b', output):
            issues.append("Potential SSN detected — masked")
            output = re.sub(r'\b\d{3}[-.]?\d{2}[-.]?\d{4}\b', '***-**-****', output)

        # Email masking (in non-code contexts)
        emails = re.findall(r'\b[\w.-]+@[\w.-]+\.\w+\b', output)
        if emails:
            for email in emails:
                if not any(code_marker in output for code_marker in ['```', '`' + email + '`']):
                    issues.append("Email address detected — consider if appropriate")

        return {
            "safe": len(issues) == 0,
            "issues": issues,
            "output": output,
        }


class GuardrailSystem:
    """Combined input/output guardrail system."""

    def __init__(self, blocked_patterns: list[str] | None = None):
        self.input_guard = InputGuardrail(
            max_length=2000,
            blocked_patterns=blocked_patterns or []
        )
        self.output_guard = OutputGuardrail(max_length=5000)
        self.stats = {"inputs_checked": 0, "inputs_blocked": 0, "outputs_checked": 0, "outputs_modified": 0}

    def check_input(self, user_input: str) -> dict:
        self.stats["inputs_checked"] += 1
        result = self.input_guard.validate(user_input)
        if not result["safe"]:
            self.stats["inputs_blocked"] += 1
        return result

    def check_output(self, output: str) -> dict:
        self.stats["outputs_checked"] += 1
        result = self.output_guard.validate(output)
        if not result["safe"]:
            self.stats["outputs_modified"] += 1
        return result

    def get_stats(self) -> dict:
        return self.stats
