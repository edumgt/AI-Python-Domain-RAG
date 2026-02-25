import os
import uuid

from app.core.config import settings
from app.services.chunker import TextChunker
from app.services.embedder import EmbeddingService
from app.services.file_parser import FileParser
from app.services.llm_service import LLMService
from app.services.vector_store import VectorStore


class RAGService:
    def __init__(self):
        self.parser = FileParser()
        self.chunker = TextChunker()
        self.embedder = EmbeddingService(settings.embedding_model)
        self.vector_store = VectorStore()
        self.llm = LLMService()

    def ingest_text(self, document_id: str, title: str, content: str):
        chunks = self.chunker.split_text(content)
        if not chunks:
            return 0

        chunk_docs = []
        for idx, chunk in enumerate(chunks):
            chunk_docs.append(
                {
                    "chunk_id": f"{document_id}-chunk-{idx}",
                    "document_id": document_id,
                    "title": title,
                    "content": chunk,
                    "chunk_index": idx,
                }
            )

        vectors = self.embedder.embed_texts([c["content"] for c in chunk_docs])
        self.vector_store.upsert_chunks(chunk_docs, vectors)
        return len(chunk_docs)

    def ingest_file(self, saved_path: str, original_filename: str):
        text = self.parser.parse_file(saved_path)
        document_id = str(uuid.uuid4())
        title = original_filename
        count = self.ingest_text(document_id=document_id, title=title, content=text)
        return {
            "document_id": document_id,
            "title": title,
            "chunks": count,
            "text_length": len(text),
        }

    def save_upload_file(self, filename: str, file_bytes: bytes) -> str:
        os.makedirs(settings.upload_dir, exist_ok=True)
        safe_name = f"{uuid.uuid4()}_{filename}"
        save_path = os.path.join(settings.upload_dir, safe_name)

        with open(save_path, "wb") as f:
            f.write(file_bytes)

        return save_path

    def ask(self, question: str, top_k: int | None = None):
        final_top_k = top_k or settings.top_k
        query_vector = self.embedder.embed_query(question)
        results = self.vector_store.search(query_vector=query_vector, top_k=final_top_k)

        chunks = []
        for item in results:
            chunks.append(
                {
                    "chunk_id": item.payload.get("chunk_id", ""),
                    "document_id": item.payload.get("document_id", ""),
                    "title": item.payload.get("title", ""),
                    "content": item.payload.get("content", ""),
                    "score": float(item.score),
                }
            )

        answer = self.llm.generate_answer(question, chunks)
        return answer, chunks
