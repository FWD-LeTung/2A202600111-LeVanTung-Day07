from typing import Callable
from .store import EmbeddingStore

class KnowledgeBaseAgent:
    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        """
        Quy trình RAG: Truy xuất -> Xây dựng Prompt -> Gọi LLM.
        """
        # 1. Truy xuất các đoạn văn bản liên quan
        results = self.store.search(question, top_k=top_k)
        
        # 2. Xây dựng context từ các chunk tìm được
        context_parts = [res["content"] for res in results]
        context_text = "\n---\n".join(context_parts)
        
        # 3. Tạo prompt gửi cho LLM
        prompt = f"""Bạn là một trợ lý hỗ trợ dựa trên kiến thức được cung cấp. 
Hãy trả lời câu hỏi sau dựa TRỰC TIẾP trên các đoạn văn bản được trích dẫn. 
Nếu không có thông tin trong ngữ cảnh, hãy trả lời là bạn không biết.

NGỮ CẢNH:
{context_text}

CÂU HỎI: {question}

TRẢ LỜI:"""
        
        return self.llm_fn(prompt)