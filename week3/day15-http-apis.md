# Day 15: HTTP Requests & REST APIs

## Learning Goals
- Understand HTTP methods (GET, POST, PUT, DELETE)
- Use the `requests` library to call APIs
- Parse JSON responses
- Handle API errors and status codes

---

## 1. HTTP Basics

```
Client  ──── Request ────>  Server
        <─── Response ────
```

| Method | Purpose | Example |
|--------|---------|---------|
| `GET` | Retrieve data | Get a list of models |
| `POST` | Send/create data | Send a prompt for completion |
| `PUT` | Update data | Update agent configuration |
| `DELETE` | Remove data | Delete a conversation |

---

## 2. Making Requests with `requests`

```bash
pip install requests
```

```python
import requests

# GET request
response = requests.get("https://jsonplaceholder.typicode.com/posts/1")

print(response.status_code)    # 200
print(response.headers["content-type"])  # application/json
print(response.json())         # Parse JSON body to Python dict

# POST request
data = {
    "title": "My Post",
    "body": "Hello from Python!",
    "userId": 1
}
response = requests.post(
    "https://jsonplaceholder.typicode.com/posts",
    json=data  # Automatically sets Content-Type: application/json
)
print(response.status_code)  # 201 (Created)
print(response.json())
```

---

## 3. Headers and Authentication

```python
import requests

# API Key in headers (most common for AI APIs)
headers = {
    "Authorization": "Bearer sk-your-api-key-here",
    "Content-Type": "application/json",
}

response = requests.post(
    "https://api.example.com/v1/completions",
    headers=headers,
    json={"prompt": "Hello", "model": "gpt-4"}
)

# Basic Authentication
response = requests.get(
    "https://api.example.com/data",
    auth=("username", "password")
)
```

---

## 4. Status Codes

```python
import requests

response = requests.get("https://jsonplaceholder.typicode.com/posts/1")

# Check status
if response.status_code == 200:
    print("Success!")
elif response.status_code == 404:
    print("Not found!")
elif response.status_code == 429:
    print("Rate limited! Slow down.")
elif response.status_code >= 500:
    print("Server error!")

# Or use raise_for_status()
try:
    response.raise_for_status()  # Raises HTTPError for 4xx/5xx
    data = response.json()
except requests.exceptions.HTTPError as e:
    print(f"HTTP Error: {e}")
except requests.exceptions.ConnectionError:
    print("Failed to connect!")
except requests.exceptions.Timeout:
    print("Request timed out!")
```

| Code Range | Meaning |
|-----------|---------|
| 200-299 | Success |
| 400 | Bad request |
| 401 | Unauthorized (bad API key) |
| 403 | Forbidden |
| 404 | Not found |
| 429 | Rate limited |
| 500-599 | Server error |

---

## 5. Query Parameters and Timeouts

```python
import requests

# Query parameters
params = {
    "q": "Python AI agents",
    "page": 1,
    "per_page": 10
}
response = requests.get(
    "https://api.github.com/search/repositories",
    params=params,
    timeout=10  # Timeout after 10 seconds
)
data = response.json()
print(f"Found {data['total_count']} repositories")

for repo in data["items"][:5]:
    print(f"  {repo['full_name']} ⭐ {repo['stargazers_count']}")
```

---

## 6. Practical: API Client Class

```python
import requests
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api_client")

class APIClient:
    """A reusable REST API client with retry logic."""
    
    def __init__(self, base_url: str, api_key: str | None = None, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        
        if api_key:
            self.session.headers["Authorization"] = f"Bearer {api_key}"
        self.session.headers["Content-Type"] = "application/json"
    
    def _request(self, method: str, endpoint: str, retries: int = 3, **kwargs) -> dict:
        """Make an HTTP request with retry logic."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        for attempt in range(1, retries + 1):
            try:
                logger.info(f"[Attempt {attempt}] {method} {url}")
                response = self.session.request(
                    method, url, timeout=self.timeout, **kwargs
                )
                response.raise_for_status()
                return response.json()
            
            except requests.exceptions.HTTPError as e:
                if response.status_code == 429:
                    wait = 2 ** attempt
                    logger.warning(f"Rate limited. Waiting {wait}s...")
                    time.sleep(wait)
                elif response.status_code >= 500:
                    logger.warning(f"Server error. Retrying...")
                    time.sleep(1)
                else:
                    raise
            
            except requests.exceptions.ConnectionError:
                logger.warning(f"Connection failed. Retrying...")
                time.sleep(2 ** attempt)
        
        raise Exception(f"Failed after {retries} attempts: {method} {url}")
    
    def get(self, endpoint: str, params: dict | None = None) -> dict:
        return self._request("GET", endpoint, params=params)
    
    def post(self, endpoint: str, data: dict | None = None) -> dict:
        return self._request("POST", endpoint, json=data)
    
    def put(self, endpoint: str, data: dict | None = None) -> dict:
        return self._request("PUT", endpoint, json=data)
    
    def delete(self, endpoint: str) -> dict:
        return self._request("DELETE", endpoint)

# Usage
client = APIClient("https://jsonplaceholder.typicode.com")

# GET
posts = client.get("/posts", params={"userId": 1})
print(f"Found {len(posts)} posts")

# POST
new_post = client.post("/posts", data={
    "title": "AI Agent Tutorial",
    "body": "Building agents with Python...",
    "userId": 1
})
print(f"Created post: {new_post}")
```

---

## 7. Working with GitHub API (Real Example)

```python
import requests

def search_github_repos(query: str, language: str = "python", limit: int = 5):
    """Search GitHub for repositories."""
    response = requests.get(
        "https://api.github.com/search/repositories",
        params={
            "q": f"{query} language:{language}",
            "sort": "stars",
            "order": "desc",
            "per_page": limit
        },
        timeout=10
    )
    response.raise_for_status()
    data = response.json()
    
    results = []
    for repo in data["items"]:
        results.append({
            "name": repo["full_name"],
            "stars": repo["stargazers_count"],
            "description": repo["description"],
            "url": repo["html_url"]
        })
    
    return results

# Search for AI agent frameworks
repos = search_github_repos("AI agent framework")
for repo in repos:
    print(f"⭐ {repo['stars']:>6} | {repo['name']}")
    print(f"         {repo['description'][:60]}")
    print()
```

---

## 8. Exercises

### Exercise 1: Weather API Client
```python
# Using the free wttr.in API (no key needed):
# https://wttr.in/London?format=j1
# 
# 1. Build a function get_weather(city) that returns temperature, condition
# 2. Handle errors (city not found, network issues)
# 3. Cache results to avoid repeated calls for the same city
```

### Exercise 2: REST API Wrapper
```python
# Build a wrapper for jsonplaceholder.typicode.com:
# 1. list_posts(user_id=None) — GET /posts, optionally filter by user
# 2. get_post(post_id) — GET /posts/{id}
# 3. create_post(title, body, user_id) — POST /posts
# 4. get_comments(post_id) — GET /posts/{id}/comments
# 5. Add proper error handling and return typed dicts
```

### Exercise 3: API Health Checker
```python
# Build a tool that checks the health of multiple APIs:
# 1. Takes a list of URLs
# 2. Makes a GET request to each
# 3. Records: status code, response time, whether it's healthy
# 4. Prints a summary table
# 5. Flags any endpoints that are down or slow (>2 seconds)
# Test with real URLs: jsonplaceholder, github api, httpbin.org
```

---

## Solutions

See [solutions/day15_solutions.py](../solutions/day15_solutions.py)

---

## Key Takeaways
- `requests` is the standard library for HTTP calls in Python
- Use `response.json()` to parse JSON responses
- Always set `timeout` and handle exceptions
- Build retry logic for unreliable APIs (common in AI)
- `requests.Session()` reuses connections and headers
- Status code 429 = rate limited; implement exponential backoff

**Tomorrow:** Environment variables and secrets management →
