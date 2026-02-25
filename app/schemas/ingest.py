from pydantic import BaseModel


class IngestTextRequest(BaseModel):
    document_id: str
    title: str
    content: str
