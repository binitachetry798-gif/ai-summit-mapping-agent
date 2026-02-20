from fastapi import APIRouter, UploadFile, File, HTTPException
from models.schemas import VerifyDocumentResponse
from services.ocr import verify_document

router = APIRouter(prefix="/verify", tags=["Document Verification"])


@router.post("/document", response_model=VerifyDocumentResponse, summary="Verify Udyam/GST certificate via OCR")
async def verify_doc(file: UploadFile = File(..., description="Upload Udyam Certificate or GST Certificate (PDF or image)")):
    """
    Scans uploaded Udyam Registration Certificate or GSTIN document using OCR.
    Extracts: Udyam Number, GSTIN, PAN, Enterprise Name, Owner Name, Registration Date.
    Returns extracted fields and verification confidence score.
    """
    allowed_types = [
        "application/pdf", "image/jpeg", "image/png",
        "image/tiff", "image/bmp", "image/jpg"
    ]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type '{file.content_type}'. Please upload PDF or image."
        )

    file_bytes = await file.read()
    if len(file_bytes) > 10 * 1024 * 1024:  # 10 MB limit
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 10MB.")

    result = verify_document(file_bytes, file.filename or "unknown")
    return VerifyDocumentResponse(**result)
