from fastapi import APIRouter, HTTPException

from ai_core.gemini_generator import GeminiDocumentGenerator
from backend.schemas import DocumentRequest, DocumentResponse


router = APIRouter()

generator = GeminiDocumentGenerator()


@router.get("/health")
def health():

    return {
        "status": "ok",
        "demo_mode": generator.demo_mode,
        "model": generator.model_name,
        "api_key_configured": generator.api_key_configured
    }


@router.post(
    "/generate",
    response_model=DocumentResponse
)
def generate_document(request: DocumentRequest):

    try:

        document = generator.generate_document(
            document_type=request.document_type,
            parties=request.parties,
            terms=request.terms,
            effective_date=request.effective_date
        )

        return DocumentResponse(
            document=document
        )

    except Exception as exc:

        raise HTTPException(
            status_code=502,
            detail=str(exc)
        ) from exc