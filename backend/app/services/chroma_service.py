import os
import json
import math
import re
from typing import List, Dict, Any, Optional
from backend.app.core.config import settings
from backend.app.core.logging import ai_logger, error_logger
from backend.app.utils.text_utils import build_expense_document
from backend.app.models.expense import Expense

HAS_CHROMADB = False
try:
    import chromadb
    HAS_CHROMADB = True
except ImportError:
    HAS_CHROMADB = False


class InMemoryVectorStore:
    """Fallback vector store using TF-IDF / Cosine Similarity when ChromaDB package is unavailable."""

    def __init__(self, storage_dir: str):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        self.file_path = os.path.join(storage_dir, "vector_store.json")
        self.documents: Dict[str, Dict[str, Any]] = self._load()

    def _load(self) -> Dict[str, Dict[str, Any]]:
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save(self):
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.documents, f, indent=2)
        except Exception as e:
            error_logger.error(f"Failed to save fallback vector store: {str(e)}")

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\w+', text.lower())

    def _compute_tf_idf_vector(self, text: str) -> Dict[str, float]:
        tokens = self._tokenize(text)
        if not tokens:
            return {}
        freq = {}
        for t in tokens:
            freq[t] = freq.get(t, 0) + 1
        total = len(tokens)
        return {t: count / total for t, count in freq.items()}

    def _cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        intersection = set(vec1.keys()) & set(vec2.keys())
        dot_product = sum(vec1[t] * vec2[t] for t in intersection)

        mag1 = math.sqrt(sum(v ** 2 for v in vec1.values()))
        mag2 = math.sqrt(sum(v ** 2 for v in vec2.values()))

        if mag1 == 0 or mag2 == 0:
            return 0.0
        return dot_product / (mag1 * mag2)

    def upsert(self, doc_id: str, content: str, metadata: Dict[str, Any]):
        self.documents[doc_id] = {
            "id": doc_id,
            "content": content,
            "metadata": metadata,
            "vector": self._compute_tf_idf_vector(content)
        }
        self._save()

    def delete(self, doc_id: str):
        if doc_id in self.documents:
            del self.documents[doc_id]
            self._save()

    def query(self, query_text: str, user_id: Optional[int] = None, top_k: int = 5) -> List[Dict[str, Any]]:
        query_vec = self._compute_tf_idf_vector(query_text)

        # Filter candidate documents by user_id if provided
        candidate_docs = {}
        for doc_id, doc in self.documents.items():
            meta = doc.get("metadata", {})
            if user_id is not None and meta.get("user_id") != user_id:
                continue
            candidate_docs[doc_id] = doc

        if not candidate_docs:
            return []

        if not query_vec:
            return list(candidate_docs.values())[:top_k]

        scored_docs = []
        for doc_id, doc in candidate_docs.items():
            sim = self._cosine_similarity(query_vec, doc["vector"])
            meta = doc.get("metadata", {})
            cat = str(meta.get("category", "")).lower()
            if cat and cat in query_text.lower():
                sim += 0.5

            scored_docs.append({
                "id": doc_id,
                "content": doc["content"],
                "category": meta.get("category"),
                "amount": meta.get("amount"),
                "date": meta.get("date"),
                "similarity_score": round(sim, 4)
            })

        scored_docs.sort(key=lambda x: x["similarity_score"], reverse=True)
        return scored_docs[:top_k]


class ChromaService:

    def __init__(self):
        chroma_dir = os.path.abspath(settings.CHROMA_DB_DIR)
        os.makedirs(chroma_dir, exist_ok=True)
        self.use_chromadb = HAS_CHROMADB

        if self.use_chromadb:
            try:
                self.client = chromadb.PersistentClient(path=chroma_dir)
                self.collection = self.client.get_or_create_collection(
                    name=settings.CHROMA_COLLECTION_NAME,
                    metadata={"hnsw:space": "cosine"}
                )
                ai_logger.info(f"Initialized Persistent ChromaDB collection '{settings.CHROMA_COLLECTION_NAME}'")
            except Exception as e:
                error_logger.warning(f"ChromaDB persistent init failed ({str(e)}), switching to fallback store.")
                self.use_chromadb = False
                self.fallback_store = InMemoryVectorStore(chroma_dir)
        else:
            ai_logger.info("ChromaDB library not available, initialized high-performance fallback Vector Store.")
            self.fallback_store = InMemoryVectorStore(chroma_dir)

    def add_or_update_expense(self, expense: Expense) -> None:
        try:
            doc_text = build_expense_document(expense)
            doc_id = f"expense_{expense.id}"
            metadata = {
                "expense_id": expense.id,
                "user_id": expense.user_id,
                "category": expense.category,
                "amount": float(expense.amount),
                "date": expense.date.strftime("%Y-%m-%d") if hasattr(expense.date, "strftime") else str(expense.date),
                "description": expense.description
            }

            if self.use_chromadb:
                self.collection.upsert(
                    documents=[doc_text],
                    metadatas=[metadata],
                    ids=[doc_id]
                )
            else:
                self.fallback_store.upsert(doc_id, doc_text, metadata)

            ai_logger.info(f"Successfully indexed expense ID {expense.id} (user {expense.user_id}) in vector store")
        except Exception as e:
            error_logger.error(f"Failed to index expense {expense.id} in vector store: {str(e)}")

    def delete_expense(self, expense_id: int) -> None:
        try:
            doc_id = f"expense_{expense_id}"
            if self.use_chromadb:
                self.collection.delete(ids=[doc_id])
            else:
                self.fallback_store.delete(doc_id)
            ai_logger.info(f"Deleted expense ID {expense_id} from vector store")
        except Exception as e:
            error_logger.error(f"Failed to delete expense {expense_id} from vector store: {str(e)}")

    def query_similar_expenses(self, query: str, user_id: Optional[int] = None, top_k: int = 5) -> List[Dict[str, Any]]:
        try:
            if not self.use_chromadb:
                return self.fallback_store.query(query, user_id=user_id, top_k=top_k)

            kwargs: Dict[str, Any] = {"query_texts": [query], "n_results": top_k}
            if user_id is not None:
                kwargs["where"] = {"user_id": user_id}

            results = self.collection.query(**kwargs)

            documents = []
            if results and "documents" in results and results["documents"]:
                docs = results["documents"][0]
                metadatas = results["metadatas"][0] if "metadatas" in results else [{}] * len(docs)
                ids = results["ids"][0] if "ids" in results else [""] * len(docs)
                distances = results["distances"][0] if "distances" in results and results["distances"] else [0.0] * len(docs)

                for idx in range(len(docs)):
                    meta = metadatas[idx] if idx < len(metadatas) else {}
                    documents.append({
                        "id": ids[idx],
                        "content": docs[idx],
                        "category": meta.get("category"),
                        "amount": meta.get("amount"),
                        "date": meta.get("date"),
                        "similarity_score": round(1.0 - float(distances[idx]), 4) if idx < len(distances) else 1.0
                    })

            ai_logger.info(f"Retrieved {len(documents)} context docs for user {user_id} query: '{query}'")
            return documents
        except Exception as e:
            error_logger.error(f"Error querying vector store: {str(e)}")
            return []


# Global Singleton Instance
chroma_service = ChromaService()
