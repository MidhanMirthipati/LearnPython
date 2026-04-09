# ============================================
# Capstone Project — DevOps Assistant Agent
# Tools Module
# ============================================

import json
import random
from datetime import datetime


class ToolRegistry:
    """Registry of tools available to the agent."""

    def __init__(self):
        self._tools: dict[str, dict] = {}

    def register(self, name: str, description: str, parameters: dict, func):
        self._tools[name] = {
            "func": func,
            "schema": {
                "type": "function",
                "function": {
                    "name": name,
                    "description": description,
                    "parameters": parameters,
                }
            }
        }

    def get_schemas(self) -> list[dict]:
        return [t["schema"] for t in self._tools.values()]

    def execute(self, name: str, arguments: dict) -> str:
        if name not in self._tools:
            return json.dumps({"error": f"Tool '{name}' not found"})
        try:
            result = self._tools[name]["func"](**arguments)
            return json.dumps(result, default=str)
        except Exception as e:
            return json.dumps({"error": str(e)})

    def list_tools(self) -> list[dict]:
        return [
            {"name": name, "description": t["schema"]["function"]["description"]}
            for name, t in self._tools.items()
        ]


# --- Tool Implementations ---

def check_server_status(hostname: str, port: int = 443) -> dict:
    """Check the health status of a server."""
    statuses = ["healthy", "healthy", "healthy", "degraded", "down"]
    return {
        "hostname": hostname,
        "port": port,
        "status": random.choice(statuses),
        "latency_ms": random.randint(5, 500),
        "uptime": f"{random.randint(1, 365)} days",
        "checked_at": datetime.now().isoformat(),
    }


def docker_status(container_name: str = "all") -> dict:
    """Get Docker container status."""
    containers = {
        "web-app": {"status": "running", "cpu": "12%", "memory": "256MB", "ports": "8080:80"},
        "database": {"status": "running", "cpu": "8%", "memory": "512MB", "ports": "5432:5432"},
        "redis": {"status": "running", "cpu": "2%", "memory": "64MB", "ports": "6379:6379"},
        "worker": {"status": "stopped", "cpu": "0%", "memory": "0MB", "ports": "-"},
    }
    if container_name == "all":
        return {"containers": containers, "total": len(containers)}
    return containers.get(container_name, {"error": f"Container '{container_name}' not found"})


def k8s_cluster_info(namespace: str = "default") -> dict:
    """Get Kubernetes cluster information."""
    return {
        "namespace": namespace,
        "pods": [
            {"name": "api-deployment-abc12", "status": "Running", "restarts": 0, "age": "2d"},
            {"name": "api-deployment-def34", "status": "Running", "restarts": 1, "age": "2d"},
            {"name": "worker-deployment-ghi56", "status": "CrashLoopBackOff", "restarts": 15, "age": "1d"},
        ],
        "services": [
            {"name": "api-service", "type": "ClusterIP", "port": 80},
            {"name": "api-external", "type": "LoadBalancer", "port": 443},
        ],
        "nodes": 3,
        "total_pods": 3,
    }


def check_ci_pipeline(repo: str = "main") -> dict:
    """Check CI/CD pipeline status."""
    stages = ["build", "test", "security-scan", "deploy-staging"]
    pipeline_status = random.choice(["passed", "passed", "failed"])
    return {
        "repo": repo,
        "branch": "main",
        "status": pipeline_status,
        "stages": [
            {"name": s, "status": "passed" if pipeline_status == "passed" or i < 2 else random.choice(["passed", "failed"])}
            for i, s in enumerate(stages)
        ],
        "duration": f"{random.randint(2, 15)}m {random.randint(0, 59)}s",
        "triggered_by": "push to main",
        "last_run": datetime.now().isoformat(),
    }


def analyze_logs(service: str, level: str = "ERROR", last_n: int = 5) -> dict:
    """Analyze recent logs for a service."""
    log_messages = {
        "ERROR": [
            "Connection timeout to database after 30s",
            "Out of memory: killed process api-worker",
            "SSL certificate expired for api.example.com",
            "Rate limit exceeded: 429 Too Many Requests",
            "Disk space critically low: 95% used",
        ],
        "WARNING": [
            "High memory usage: 85%",
            "Slow query detected: 2.5s",
            "Certificate expires in 7 days",
            "Connection pool near capacity: 90%",
            "Retry attempt 3/5 for external API",
        ],
    }

    messages = log_messages.get(level, log_messages["ERROR"])
    selected = random.sample(messages, min(last_n, len(messages)))

    return {
        "service": service,
        "level": level,
        "entries": [
            {"timestamp": datetime.now().isoformat(), "level": level, "message": msg}
            for msg in selected
        ],
        "total_matching": random.randint(last_n, last_n * 10),
    }


def calculate_cost(service: str, hours: int = 24) -> dict:
    """Estimate cloud infrastructure costs."""
    rates = {"compute": 0.10, "storage": 0.02, "network": 0.05, "database": 0.15}
    costs = {k: round(v * hours * random.uniform(0.8, 1.2), 2) for k, v in rates.items()}
    total = round(sum(costs.values()), 2)
    return {
        "service": service,
        "period_hours": hours,
        "breakdown": costs,
        "total": f"${total}",
        "projected_monthly": f"${round(total * 30, 2)}",
    }


# --- Build Default Registry ---

def create_default_registry() -> ToolRegistry:
    """Create and populate the default tool registry."""
    registry = ToolRegistry()

    registry.register(
        "check_server", "Check the health and status of a server",
        {"type": "object", "properties": {
            "hostname": {"type": "string", "description": "Server hostname or IP"},
            "port": {"type": "integer", "description": "Port to check", "default": 443},
        }, "required": ["hostname"]},
        check_server_status
    )

    registry.register(
        "docker_status", "Get Docker container status and resource usage",
        {"type": "object", "properties": {
            "container_name": {"type": "string", "description": "Container name or 'all'", "default": "all"},
        }},
        docker_status
    )

    registry.register(
        "k8s_info", "Get Kubernetes cluster information for a namespace",
        {"type": "object", "properties": {
            "namespace": {"type": "string", "description": "K8s namespace", "default": "default"},
        }},
        k8s_cluster_info
    )

    registry.register(
        "ci_pipeline", "Check CI/CD pipeline status for a repository",
        {"type": "object", "properties": {
            "repo": {"type": "string", "description": "Repository name", "default": "main"},
        }},
        check_ci_pipeline
    )

    registry.register(
        "analyze_logs", "Search and analyze logs for a specific service",
        {"type": "object", "properties": {
            "service": {"type": "string", "description": "Service name"},
            "level": {"type": "string", "enum": ["ERROR", "WARNING", "INFO"], "default": "ERROR"},
            "last_n": {"type": "integer", "description": "Number of log entries", "default": 5},
        }, "required": ["service"]},
        analyze_logs
    )

    registry.register(
        "calculate_cost", "Estimate infrastructure costs for a service",
        {"type": "object", "properties": {
            "service": {"type": "string", "description": "Service/project name"},
            "hours": {"type": "integer", "description": "Time period in hours", "default": 24},
        }, "required": ["service"]},
        calculate_cost
    )

    return registry
