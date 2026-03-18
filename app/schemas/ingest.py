from pydantic import BaseModel
from app.schemas.chat import DomainType


class IngestTextRequest(BaseModel):
    document_id: str
    title: str
    content: str
    domain: DomainType = DomainType.general
