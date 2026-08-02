from typing import List, Optional
from pydantic import BaseModel, Field


class ContextDocument(BaseModel):
    id: str
    content: str
    category: Optional[str] = None
    amount: Optional[float] = None
    date: Optional[str] = None
    similarity_score: Optional[float] = None


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=500, description="Financial question for AI")


class ChatResponse(BaseModel):
    question: str
    answer: str
    retrieved_documents: List[ContextDocument] = []
    model_used: str = "llama3"
    is_fallback: bool = False
    processing_time_ms: float = 0.0
