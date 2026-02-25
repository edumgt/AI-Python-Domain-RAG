from typing import List
from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str
    top_k: int | None = None


class RetrievedChunk(BaseModel):
    chunk_id: str
    document_id: str
    title: str
    content: str
    score: float


class ChatResponse(BaseModel):
    answer: str
    references: List[RetrievedChunk]
