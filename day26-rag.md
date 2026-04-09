# Day 26: RAG — Retrieval Augmented Generation

## Learning Goals
- Understand what RAG is and why it matters
- Create text embeddings
- Build a vector store
- Implement a complete RAG pipeline

---

## 1. What is RAG?

**Problem:** LLMs only know what they were trained on. They can't access your documentation, logs, or private data.

**Solution:** RAG = Retrieval Augmented Generation
1. **Store** your documents in a vector database
2. **Retrieve** relevant chunks based on user query
3. **Augment** the LLM prompt with retrieved context
4. **Generate** an answer grounded in your data

```
User Query
    │
    ▼
[Embed Query] → [Search Vector DB] → [Get Relevant Chunks]
                                            │
                                            ▼
                              [Build Prompt: System + Context + Query]
                                            │
                                            ▼
                                    [LLM Generates Answer]
```

---

## 2. Text Embeddings

Embeddings convert text into numerical vectors. Both OpenAI and Google Gemini provide embedding models (**Anthropic does not offer its own embedding API** — use OpenAI or Gemini embeddings with Claude).

### OpenAI Embeddings
```python
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

def get_embedding_openai(text: str, model: str = "text-embedding-3-small") -> list[float]:
    """Get embedding vector using OpenAI."""
    response = client.embeddings.create(input=text, model=model)
    return response.data[0].embedding

embedding = get_embedding_openai("How to deploy to Kubernetes")
print(f"Dimensions: {len(embedding)}")  # 1536
```

### Google Gemini Embeddings
```python
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure()

def get_embedding_gemini(text: str, model: str = "models/text-embedding-004") -> list[float]:
    """Get embedding vector using Google Gemini."""
    result = genai.embed_content(model=model, content=text)
    return result["embedding"]

embedding = get_embedding_gemini("How to deploy to Kubernetes")
print(f"Dimensions: {len(embedding)}")  # 768
```

> **Note:** You can use any embedding provider with any LLM for the generation step. For example, use Google embeddings for retrieval but Claude for answer generation.

### What Are Embeddings?
- An embedding converts text into a list of numbers (vector)
- Similar texts have similar vectors
- You can calculate "distance" between texts using their vectors
- This enables semantic search: finding relevant content by meaning, not keywords

---

## 3. Building a Simple Vector Store

```python
import numpy as np
from dotenv import load_dotenv
import os

load_dotenv()

class SimpleVectorStore:
    """A minimal vector store that works with OpenAI or Gemini embeddings."""
    
    def __init__(self, embedding_provider: str = "openai"):
        self.documents: list[dict] = []
        self.embeddings: list[list[float]] = []
        self.embedding_provider = embedding_provider
        
        if embedding_provider == "openai":
            from openai import OpenAI
            self._client = OpenAI()
        elif embedding_provider == "gemini":
            import google.generativeai as genai
            genai.configure()
            self._genai = genai
    
    def add_document(self, text: str, metadata: dict | None = None):
        """Add a document to the store."""
        embedding = self._get_embedding(text)
        self.documents.append({
            "text": text,
            "metadata": metadata or {},
            "id": len(self.documents)
        })
        self.embeddings.append(embedding)
    
    def _get_embedding(self, text: str) -> list[float]:
        if self.embedding_provider == "openai":
            response = self._client.embeddings.create(
                input=text, model="text-embedding-3-small"
            )
            return response.data[0].embedding
        elif self.embedding_provider == "gemini":
            result = self._genai.embed_content(
                model="models/text-embedding-004", content=text
            )
            return result["embedding"]
    
    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        a_arr = np.array(a)
        b_arr = np.array(b)
        return float(np.dot(a_arr, b_arr) / (np.linalg.norm(a_arr) * np.linalg.norm(b_arr)))
    
    def search(self, query: str, top_k: int = 3) -> list[dict]:
        """Search for most similar documents."""
        query_embedding = self._get_embedding(query)
        
        similarities = []
        for i, doc_embedding in enumerate(self.embeddings):
            sim = self._cosine_similarity(query_embedding, doc_embedding)
            similarities.append((i, sim))
        
        # Sort by similarity (highest first)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for idx, score in similarities[:top_k]:
            results.append({
                **self.documents[idx],
                "score": round(score, 4)
            })
        
        return results

# Usage
store = SimpleVectorStore()

# Add DevOps documentation
docs = [
    "Docker is a platform for containerizing applications. Use 'docker build' to create images and 'docker run' to start containers.",
    "Kubernetes (K8s) orchestrates containers across clusters. Key concepts: Pods, Services, Deployments, and Ingress.",
    "Terraform is an Infrastructure as Code tool. Write .tf files to define infrastructure and use 'terraform apply' to deploy.",
    "GitHub Actions automates CI/CD workflows. Define workflows in .github/workflows/ using YAML files.",
    "Prometheus collects metrics from services. Grafana visualizes them. Together they form a monitoring stack.",
    "Ansible automates configuration management using YAML playbooks. It connects to servers via SSH.",
    "Helm is a package manager for Kubernetes. Charts are reusable templates for K8s manifests.",
    "ArgoCD implements GitOps for Kubernetes. It syncs your K8s cluster state with Git repositories.",
]

for doc in docs:
    store.add_document(doc, metadata={"source": "devops_docs"})

# Search
results = store.search("How do I deploy my app to a Kubernetes cluster?")
for r in results:
    print(f"[{r['score']}] {r['text'][:80]}...")
```

---

## 4. Document Chunking

```python
def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Try to break at sentence boundary
        if end < len(text):
            # Look for period near the end
            last_period = text[start:end].rfind(". ")
            if last_period > chunk_size * 0.5:
                end = start + last_period + 1
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end - overlap
    
    return chunks

# Example
long_doc = """Docker is a platform for developing, shipping, and running applications. 
It enables you to separate your applications from your infrastructure. Docker provides 
the ability to package and run an application in a loosely isolated environment called a 
container. Containers are lightweight and contain everything needed to run the application.

Kubernetes, on the other hand, is a container orchestration platform. While Docker runs 
individual containers, Kubernetes manages clusters of containers across multiple machines. 
It handles scaling, load balancing, and self-healing of containerized applications.

Together, Docker and Kubernetes form the foundation of modern cloud-native development. 
Docker packages your app, and Kubernetes runs it at scale."""

chunks = chunk_text(long_doc, chunk_size=200, overlap=30)
for i, chunk in enumerate(chunks):
    print(f"Chunk {i}: {chunk[:60]}... ({len(chunk)} chars)")
```

---

## 5. Using ChromaDB (Production Vector Store)

```python
import chromadb
from chromadb.utils import embedding_functions

chroma_client = chromadb.Client()  # In-memory
# Or persist to disk:
# chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Choose your embedding provider:

# Option A: OpenAI embeddings
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    model_name="text-embedding-3-small"
)

# Option B: Google Gemini embeddings
# google_ef = embedding_functions.GoogleGenerativeAiEmbeddingFunction(
#     model_name="models/text-embedding-004"
# )

collection = chroma_client.create_collection(
    name="devops_knowledge",
    embedding_function=openai_ef  # or google_ef
)

# Add documents
collection.add(
    documents=[
        "Docker containers share the host OS kernel, making them lightweight.",
        "Kubernetes pods can contain one or more containers.",
        "Terraform state files track the current state of your infrastructure.",
        "GitHub Actions workflows are triggered by events like push or PR.",
    ],
    ids=["doc1", "doc2", "doc3", "doc4"],
    metadatas=[
        {"topic": "docker"}, {"topic": "kubernetes"},
        {"topic": "terraform"}, {"topic": "cicd"}
    ]
)

# Query
results = collection.query(
    query_texts=["How do containers work?"],
    n_results=2
)

for doc, score in zip(results["documents"][0], results["distances"][0]):
    print(f"[{score:.4f}] {doc}")
```

---

## 6. Complete RAG Pipeline

```python
from dotenv import load_dotenv
import os
import chromadb
from chromadb.utils import embedding_functions

load_dotenv()

class RAGAgent:
    """Agent with Retrieval Augmented Generation — supports OpenAI, Anthropic, and Gemini."""
    
    def __init__(self, collection_name: str = "knowledge_base", llm_provider: str = "openai"):
        self.llm_provider = llm_provider
        self.chroma = chromadb.Client()
        
        # Use OpenAI embeddings by default (works regardless of LLM provider)
        openai_ef = embedding_functions.OpenAIEmbeddingFunction(
            model_name="text-embedding-3-small"
        )
        
        self.collection = self.chroma.create_collection(
            name=collection_name,
            embedding_function=openai_ef
        )
        self.doc_count = 0
        
        # Initialize LLM client
        if llm_provider == "openai":
            from openai import OpenAI
            self.client = OpenAI()
            self.model = "gpt-4o-mini"
        elif llm_provider == "anthropic":
            import anthropic
            self.client = anthropic.Anthropic()
            self.model = "claude-sonnet-4-20250514"
        elif llm_provider == "gemini":
            import google.generativeai as genai
            genai.configure()
            self._genai_model = genai.GenerativeModel("gemini-2.0-flash")
            self.model = "gemini-2.0-flash"
    
    def add_knowledge(self, documents: list[str], metadatas: list[dict] | None = None):
        """Add documents to the knowledge base."""
        ids = [f"doc_{self.doc_count + i}" for i in range(len(documents))]
        
        self.collection.add(
            documents=documents,
            ids=ids,
            metadatas=metadatas
        )
        self.doc_count += len(documents)
        print(f"Added {len(documents)} documents. Total: {self.doc_count}")
    
    def retrieve(self, query: str, n_results: int = 3) -> list[str]:
        """Retrieve relevant documents for a query."""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results["documents"][0]
    
    def ask(self, question: str) -> str:
        """Answer a question using RAG — works with any LLM provider."""
        context_docs = self.retrieve(question)
        context = "\n\n".join(f"[{i+1}] {doc}" for i, doc in enumerate(context_docs))
        
        system_prompt = """You are a helpful assistant. Answer questions based on the provided context.
If the context doesn't contain enough information, say so.
Cite which context piece(s) you used, e.g., [1], [2]."""
        
        user_prompt = f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer based on the context above:"
        
        if self.llm_provider == "openai":
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3, max_tokens=500
            )
            return response.choices[0].message.content
        
        elif self.llm_provider == "anthropic":
            response = self.client.messages.create(
                model=self.model, max_tokens=500,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
                temperature=0.3
            )
            return response.content[0].text
        
        elif self.llm_provider == "gemini":
            response = self._genai_model.generate_content(
                f"{system_prompt}\n\n{user_prompt}",
                generation_config={"temperature": 0.3, "max_output_tokens": 500}
            )
            return response.text

# --- Build and use (change provider to "anthropic" or "gemini" to switch) ---
provider = os.environ.get("LLM_PROVIDER", "openai")
rag = RAGAgent(llm_provider=provider)

# Add DevOps knowledge base
rag.add_knowledge([
    "To create a Docker image, write a Dockerfile and run 'docker build -t myapp .'. Best practice: use multi-stage builds to reduce image size.",
    "Kubernetes Deployments manage ReplicaSets which manage Pods. Use 'kubectl apply -f deployment.yaml' to create. Spec includes replicas, selector, and template.",
    "Terraform modules are reusable infrastructure components. Structure: main.tf (resources), variables.tf (inputs), outputs.tf (outputs). Use 'terraform init' then 'terraform apply'.",
    "GitHub Actions workflows go in .github/workflows/. Key concepts: triggers (on), jobs, steps, actions. Use 'actions/checkout@v4' to check out code.",
    "Horizontal Pod Autoscaler (HPA) automatically scales pods based on CPU/memory. Command: 'kubectl autoscale deployment myapp --cpu-percent=50 --min=2 --max=10'.",
    "Docker Compose defines multi-container apps in docker-compose.yml. Services, networks, and volumes. Run with 'docker compose up -d'.",
    "Secrets in Kubernetes are base64-encoded and stored as K8s objects. Better: use External Secrets Operator or Vault for production secrets management.",
    "CI/CD best practices: fast feedback (< 10 min builds), automated testing, infrastructure as code, blue/green deployments, monitoring and rollback capability.",
])

# Ask questions
questions = [
    "How do I scale my application automatically in Kubernetes?",
    "What's the best way to manage secrets in production?",
    "How do I set up a CI/CD pipeline?",
]

for q in questions:
    print(f"\n❓ {q}")
    answer = rag.ask(q)
    print(f"💡 {answer}\n")
    print("-" * 60)
```

---

## 7. Exercises

### Exercise 1: File-Based RAG
```python
# Build a RAG system that:
# 1. Reads all .md or .txt files from a directory
# 2. Chunks them into ~300 char segments
# 3. Stores in a vector database
# 4. Answers questions about the files
# Test with your own notes or the course markdown files
```

### Exercise 2: RAG with Sources
```python
# Enhance the RAG agent to:
# 1. Return the source document IDs with each answer
# 2. Show relevance scores
# 3. Highlight which sentences came from which source
# 4. Support follow-up questions (maintain context)
```

### Exercise 3: RAG Quality Tester
```python
# Build a test harness for your RAG system:
# 1. Define 5 question-answer pairs you know the correct answer to
# 2. Run each through the RAG system
# 3. Compare RAG answer to expected answer
# 4. Score: correct/incorrect/partial
# 5. Report accuracy metrics
```

---

## Solutions

See [solutions/day26_solutions.py](../solutions/day26_solutions.py)

---

## Key Takeaways
- RAG = Retrieve relevant docs + Augment prompt + Generate answer
- Embeddings convert text to numerical vectors for semantic comparison
- Chunk large documents into smaller pieces for better retrieval
- Embeddings: use OpenAI (`text-embedding-3-small`) or Gemini (`text-embedding-004`). Anthropic doesn't provide embeddings — pair Claude with either embedding provider.
- ChromaDB is a lightweight vector database for Python
- Always cite sources and handle "no relevant context" gracefully
- RAG lets agents answer questions about YOUR specific data

**Tomorrow:** Multi-agent systems →
