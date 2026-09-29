from typing import List, Optional

from pydantic import BaseModel


class DocumentRequest(BaseModel):
    document_type: str
    parties: str
    terms: str
    effective_date: Optional[str] = None


class DocumentResponse(BaseModel):
    document: str