# ============================================
# Day 15 Solutions — HTTP Requests & REST APIs
# ============================================

import json
from datetime import datetime


# --- Exercise 1: GitHub API Explorer ---
print("--- GitHub API Explorer ---")

# NOTE: Uses requests library. Install with: pip install requests
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("[INFO] 'requests' not installed. Using simulated data.")


def fetch_github_user(username: str) -> dict:
    """Fetch GitHub user info."""
    if not HAS_REQUESTS:
        return {
            "login": username,
            "name": f"{username} (simulated)",
            "public_repos": 42,
            "followers": 100,
            "created_at": "2020-01-01T00:00:00Z",
        }
    
    resp = requests.get(f"https://api.github.com/users/{username}", timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return {
        "login": data["login"],
        "name": data.get("name", "N/A"),
        "public_repos": data["public_repos"],
        "followers": data["followers"],
        "created_at": data["created_at"],
    }


def fetch_user_repos(username: str, limit: int = 5) -> list[dict]:
    """Fetch a user's repositories sorted by stars."""
    if not HAS_REQUESTS:
        return [
            {"name": f"repo-{i}", "stars": 100 - i * 10, "language": "Python"}
            for i in range(limit)
        ]
    
    resp = requests.get(
        f"https://api.github.com/users/{username}/repos",
        params={"sort": "updated", "per_page": limit},
        timeout=10,
    )
    resp.raise_for_status()
    return [
        {"name": r["name"], "stars": r["stargazers_count"], "language": r.get("language", "N/A")}
        for r in resp.json()
    ]


# Test
user = fetch_github_user("octocat")
print(f"User: {user['login']}")
print(f"  Name: {user['name']}")
print(f"  Repos: {user['public_repos']}")
print(f"  Followers: {user['followers']}")

repos = fetch_user_repos("octocat", 3)
print(f"\nTop repos:")
for repo in repos:
    print(f"  ⭐ {repo['stars']} | {repo['name']} ({repo['language']})")


# --- Exercise 2: REST Client Class ---
print("\n--- REST Client Class ---")


class RESTClient:
    """A reusable REST API client."""

    def __init__(self, base_url: str, headers: dict | None = None):
        self.base_url = base_url.rstrip("/")
        self.headers = headers or {}
        self.request_log: list[dict] = []

    def _log(self, method: str, url: str, status: int, elapsed: float):
        self.request_log.append({
            "method": method,
            "url": url,
            "status": status,
            "elapsed_ms": round(elapsed * 1000),
            "timestamp": datetime.now().isoformat(),
        })

    def get(self, endpoint: str, params: dict | None = None) -> dict:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        if not HAS_REQUESTS:
            self._log("GET", url, 200, 0.1)
            return {"simulated": True, "url": url}
        
        start = datetime.now()
        resp = requests.get(url, headers=self.headers, params=params, timeout=10)
        elapsed = (datetime.now() - start).total_seconds()
        self._log("GET", url, resp.status_code, elapsed)
        resp.raise_for_status()
        return resp.json()

    def post(self, endpoint: str, data: dict) -> dict:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        if not HAS_REQUESTS:
            self._log("POST", url, 201, 0.15)
            return {"simulated": True, "url": url, "data": data}
        
        start = datetime.now()
        resp = requests.post(url, headers=self.headers, json=data, timeout=10)
        elapsed = (datetime.now() - start).total_seconds()
        self._log("POST", url, resp.status_code, elapsed)
        resp.raise_for_status()
        return resp.json()

    def get_stats(self) -> dict:
        if not self.request_log:
            return {"requests": 0}
        total = len(self.request_log)
        avg_ms = sum(r["elapsed_ms"] for r in self.request_log) / total
        return {
            "total_requests": total,
            "avg_latency_ms": round(avg_ms),
            "methods": {m: sum(1 for r in self.request_log if r["method"] == m) 
                       for m in set(r["method"] for r in self.request_log)},
        }


# Test
client = RESTClient("https://jsonplaceholder.typicode.com")
result = client.get("/posts/1")
print(f"GET /posts/1: {json.dumps(result, indent=2)[:100]}...")

result = client.post("/posts", {"title": "Test", "body": "Hello", "userId": 1})
print(f"POST /posts: {json.dumps(result, indent=2)[:100]}...")

print(f"Stats: {client.get_stats()}")


# --- Exercise 3: API Health Checker ---
print("\n--- API Health Checker ---")


def check_endpoint(url: str, timeout: int = 5) -> dict:
    """Check if an API endpoint is healthy."""
    result = {
        "url": url,
        "status": "unknown",
        "status_code": None,
        "latency_ms": None,
    }

    if not HAS_REQUESTS:
        result["status"] = "healthy (simulated)"
        result["status_code"] = 200
        result["latency_ms"] = 50
        return result

    try:
        start = datetime.now()
        resp = requests.get(url, timeout=timeout)
        elapsed = (datetime.now() - start).total_seconds() * 1000
        
        result["status_code"] = resp.status_code
        result["latency_ms"] = round(elapsed)
        
        if resp.status_code < 400 and elapsed < 2000:
            result["status"] = "healthy"
        elif resp.status_code < 400:
            result["status"] = "slow"
        else:
            result["status"] = "unhealthy"

    except requests.Timeout:
        result["status"] = "timeout"
    except requests.ConnectionError:
        result["status"] = "unreachable"
    except Exception as e:
        result["status"] = f"error: {e}"

    return result


endpoints = [
    "https://api.github.com",
    "https://jsonplaceholder.typicode.com/posts/1",
    "https://httpbin.org/status/200",
]

for url in endpoints:
    result = check_endpoint(url)
    emoji = "✅" if "healthy" in result["status"] else "❌"
    print(f"  {emoji} {result['url']}")
    print(f"     Status: {result['status']} | Code: {result['status_code']} | Latency: {result['latency_ms']}ms")
