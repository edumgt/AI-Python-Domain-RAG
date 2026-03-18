from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from typing import Optional

from app.schemas.chat import DomainType
from app.schemas.ingest import IngestTextRequest
from app.services.rag_service import RAGService

router = APIRouter(prefix="/ingest", tags=["ingest"])
rag_service = RAGService()


@router.post("/text")
def ingest_text(payload: IngestTextRequest):
    count = rag_service.ingest_text(
        document_id=payload.document_id,
        title=payload.title,
        content=payload.content,
        domain=payload.domain.value,
    )
    return {
        "message": "text ingested",
        "document_id": payload.document_id,
        "chunks": count,
        "domain": payload.domain.value,
    }


@router.post("/file")
async def ingest_file(
    file: UploadFile = File(...),
    domain: Optional[DomainType] = Form(DomainType.general),
):
    filename = file.filename or "uploaded_file"

    if not (filename.lower().endswith(".txt") or filename.lower().endswith(".pdf")):
        raise HTTPException(status_code=400, detail="only .txt and .pdf files are supported")

    content = await file.read()
    saved_path = rag_service.save_upload_file(filename=filename, file_bytes=content)
    result = rag_service.ingest_file(
        saved_path=saved_path,
        original_filename=filename,
        domain=domain.value if domain else "general",
    )
    return {
        "message": "file ingested",
        **result,
    }
