from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import get_db, MSEProfile
from models.schemas import ClassifyRequest, ClassifyResponse
from services.classifier import classify_product

router = APIRouter(prefix="/classify", tags=["Classification"])


@router.post("", response_model=ClassifyResponse, summary="Classify product to ONDC taxonomy")
async def classify(request: ClassifyRequest):
    """
    Classifies a raw product description into the ONDC taxonomy.
    Returns category, subcategory, HSN code, confidence score, and keywords.
    Uses Gemini API if configured, otherwise keyword-based fallback.
    """
    if not request.description.strip():
        raise HTTPException(status_code=400, detail="Product description cannot be empty")

    result = classify_product(request.description)
    return ClassifyResponse(**result)
