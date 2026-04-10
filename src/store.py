from __future__ import annotations
from typing import Any, Callable
from .chunking import _dot, compute_similarity
from .embeddings import _mock_embed
from .models import Document

class EmbeddingStore:
    def __init__(
        self,
        collection_name: str = "documents",
        embedding_fn: Callable[[str], list[float]] | None = None,
    ) -> None:
        self._embedding_fn = embedding_fn or _mock_embed
        self._collection_name = collection_name
        self._store: list[dict[str, Any]] = []
        self._use_chroma = False

        try:
            import chromadb
            self._client = chromadb.Client()
            self._collection = self._client.get_or_create_collection(name=collection_name)
            self._use_chroma = True
        except Exception:
            self._use_chroma = False
            self._collection = None

    def _make_record(self, chunk_text: str, doc_id: str, metadata: dict) -> dict[str, Any]:
        """Tạo một bản ghi hoàn chỉnh kèm embedding."""
        combined_metadata = metadata.copy()
        combined_metadata["doc_id"] = doc_id
        return {
            "content": chunk_text,
            "embedding": self._embedding_fn(chunk_text),
            "metadata": combined_metadata
        }

    def add_documents(self, docs: list[Document]) -> None:
        """Chia nhỏ, tạo embedding và lưu trữ tài liệu."""
        from .chunking import RecursiveChunker
        chunker = RecursiveChunker(chunk_size=500)
        
        for doc in docs:
            chunks = chunker.chunk(doc.content)
            for chunk_text in chunks:
                record = self._make_record(chunk_text, doc.id, doc.metadata)
                if self._use_chroma:
                    import uuid
                    self._collection.add(
                        ids=[str(uuid.uuid4())],
                        documents=[record["content"]],
                        embeddings=[record["embedding"]],
                        metadatas=[record["metadata"]]
                    )
                else:
                    self._store.append(record)

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Tìm kiếm các đoạn văn bản tương đồng nhất với truy vấn."""
        query_vec = self._embedding_fn(query)
        
        if self._use_chroma:
            results = self._collection.query(query_embeddings=[query_vec], n_results=top_k)
            formatted = []
            for i in range(len(results["ids"][0])):
                formatted.append({
                    "content": results["documents"][0][i],
                    "score": 1.0, # Chroma trả về distance, ở đây đơn giản hóa
                    "metadata": results["metadatas"][0][i]
                })
            return formatted

        # Tìm kiếm trong bộ nhớ
        scored_records = []
        for rec in self._store:
            score = compute_similarity(query_vec, rec["embedding"])
            scored_records.append({**rec, "score": score})
        
        scored_records.sort(key=lambda x: x["score"], reverse=True)
        return scored_records[:top_k]

    def get_collection_size(self) -> int:
        if self._use_chroma:
            return self._collection.count()
        return len(self._store)

    def search_with_filter(self, query: str, top_k: int = 3, metadata_filter: dict = None) -> list[dict]:
        """Lọc dữ liệu theo metadata trước khi tìm kiếm tương đồng."""
        if not metadata_filter:
            return self.search(query, top_k)
            
        filtered_records = []
        for rec in self._store:
            match = True
            for key, val in metadata_filter.items():
                if rec["metadata"].get(key) != val:
                    match = False
                    break
            if match:
                filtered_records.append(rec)
        
        # Thực hiện search trên tập đã lọc
        query_vec = self._embedding_fn(query)
        scored = []
        for rec in filtered_records:
            score = compute_similarity(query_vec, rec["embedding"])
            scored.append({**rec, "score": score})
        
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

    def delete_document(self, doc_id: str) -> bool:
        """Xóa tất cả các chunk thuộc về một document."""
        initial_size = len(self._store)
        self._store = [rec for rec in self._store if rec["metadata"].get("doc_id") != doc_id]
        return len(self._store) < initial_size