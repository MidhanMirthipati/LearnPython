# ============================================
# Day 26 Solutions — RAG (Retrieval-Augmented Generation)
# ============================================

# NOTE: Full RAG requires: pip install chromadb langchain langchain-openai langchain-anthropic langchain-google-genai
# This file works with or without those dependencies.

import json
import os
import hashlib
from datetime import datetime

try:
    import chromadb
    HAS_CHROMADB = True
except ImportError:
    HAS_CHROMADB = False


# --- Exercise 1: Document Store ---
print("--- Document Store ---")


class Document:
    """A document with content and metadata."""

    def __init__(self, content: str, metadata: dict | None = None, doc_id: str | None = None):
        self.id = doc_id or hashlib.md5(content.encode()).hexdigest()[:12]
        self.content = content
        self.metadata = metadata or {}
        self.created_at = datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {"id": self.id, "content": self.content, "metadata": self.metadata}


class SimpleDocumentStore:
    """In-memory document store with keyword search."""

    def __init__(self):
        self.documents: dict[str, Document] = {}

    def add(self, content: str, metadata: dict | None = None) -> str:
        doc = Document(content, metadata)
        self.documents[doc.id] = doc
        return doc.id

    def add_batch(self, docs: list[dict]) -> list[str]:
        ids = []
        for doc in docs:
            doc_id = self.add(doc["content"], doc.get("metadata"))
            ids.append(doc_id)
        return ids

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        """Simple keyword-based search with scoring."""
        query_words = set(query.lower().split())
        results = []

        for doc in self.documents.values():
            doc_words = set(doc.content.lower().split())
            # Score = number of matching words
            score = len(query_words & doc_words) / max(len(query_words), 1)
            if score > 0:
                results.append({
                    "id": doc.id,
                    "content": doc.content,
                    "score": round(score, 3),
                    "metadata": doc.metadata,
                })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def delete(self, doc_id: str) -> bool:
        if doc_id in self.documents:
            del self.documents[doc_id]
            return True
        return False

    def __len__(self):
        return len(self.documents)


# Test
store = SimpleDocumentStore()

docs = [
    {"content": "Docker is a containerization platform that packages applications with their dependencies.", "metadata": {"topic": "docker", "level": "beginner"}},
    {"content": "Kubernetes orchestrates containers at scale, managing deployment, scaling, and networking.", "metadata": {"topic": "kubernetes", "level": "intermediate"}},
    {"content": "Docker Compose allows you to define multi-container applications in a YAML file.", "metadata": {"topic": "docker", "level": "beginner"}},
    {"content": "Terraform is an Infrastructure as Code tool for provisioning cloud resources.", "metadata": {"topic": "terraform", "level": "intermediate"}},
    {"content": "CI/CD pipelines automate building, testing, and deploying applications.", "metadata": {"topic": "cicd", "level": "beginner"}},
    {"content": "Helm is a package manager for Kubernetes that simplifies application deployment.", "metadata": {"topic": "kubernetes", "level": "intermediate"}},
    {"content": "Prometheus and Grafana are popular tools for monitoring container-based applications.", "metadata": {"topic": "monitoring", "level": "intermediate"}},
    {"content": "Ansible automates configuration management and application deployment across servers.", "metadata": {"topic": "ansible", "level": "beginner"}},
]

store.add_batch(docs)
print(f"Loaded {len(store)} documents\n")

# Search
queries = ["Docker containers", "Kubernetes deployment", "monitoring applications"]
for query in queries:
    results = store.search(query, top_k=2)
    print(f"Query: '{query}'")
    for r in results:
        print(f"  [{r['score']:.2f}] {r['content'][:60]}...")
    print()


# --- Exercise 2: RAG Pipeline ---
print("--- RAG Pipeline ---")


class RAGPipeline:
    """Retrieval-Augmented Generation pipeline."""

    def __init__(self, doc_store: SimpleDocumentStore):
        self.doc_store = doc_store
        self.query_log: list[dict] = []

    def retrieve(self, query: str, top_k: int = 3) -> list[dict]:
        """Retrieve relevant documents."""
        return self.doc_store.search(query, top_k)

    def build_prompt(self, query: str, context_docs: list[dict]) -> str:
        """Build a prompt with retrieved context."""
        context_text = "\n\n".join([
            f"[Source {i+1}] {doc['content']}"
            for i, doc in enumerate(context_docs)
        ])

        return f"""Answer the question based ONLY on the provided context. If the context doesn't contain enough information, say "I don't have enough information."

Context:
{context_text}

Question: {query}

Answer:"""

    def query(self, question: str, top_k: int = 3) -> dict:
        """Full RAG pipeline: retrieve → build prompt → generate."""
        # Retrieve
        docs = self.retrieve(question, top_k)

        # Build prompt
        prompt = self.build_prompt(question, docs)

        # Generate (simulated without API)
        if docs:
            answer = f"Based on the retrieved documents: {docs[0]['content'][:100]}..."
        else:
            answer = "I don't have enough information to answer that question."

        result = {
            "question": question,
            "answer": answer,
            "sources": [{"content": d["content"][:50], "score": d["score"]} for d in docs],
            "prompt_length": len(prompt),
        }

        self.query_log.append(result)
        return result


# Test
rag = RAGPipeline(store)

questions = [
    "How do I containerize my application?",
    "What tool should I use for infrastructure provisioning?",
    "How do I monitor my containers?",
]

for q in questions:
    result = rag.query(q)
    print(f"Q: {result['question']}")
    print(f"A: {result['answer'][:80]}...")
    print(f"Sources: {len(result['sources'])}")
    for src in result["sources"]:
        print(f"  [{src['score']:.2f}] {src['content']}...")
    print()


# --- Exercise 3: ChromaDB Vector Store ---
print("--- ChromaDB Vector Store ---")

if HAS_CHROMADB:
    # Use ChromaDB for real vector search
    chroma_client = chromadb.Client()
    collection = chroma_client.create_collection("devops_docs")

    # Add documents
    collection.add(
        documents=[d["content"] for d in docs],
        metadatas=[d.get("metadata", {}) for d in docs],
        ids=[f"doc_{i}" for i in range(len(docs))],
    )

    # Query
    results = collection.query(query_texts=["Docker container deployment"], n_results=3)
    print("ChromaDB results:")
    for doc, dist in zip(results["documents"][0], results["distances"][0]):
        print(f"  [{dist:.4f}] {doc[:60]}...")
else:
    print("  ChromaDB not installed. Using SimpleDocumentStore above instead.")
    print("  Install with: pip install chromadb")
    print("  The SimpleDocumentStore provides keyword search as a fallback.")
