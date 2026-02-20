"""
OCR Document Verification Service
Extracts structured data from Udyam Registration Certificates and GSTIN documents.
Uses pytesseract. Tesseract OCR must be installed on the system.
"""
import re
import io
from pathlib import Path
from typing import Optional

try:
    import pytesseract
    from PIL import Image
    # Set Tesseract path for Windows
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    OCR_AVAILABLE = True
except (ImportError, Exception):
    OCR_AVAILABLE = False

try:
    from pdf2image import convert_from_bytes
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


# ─── Regex Patterns ────────────────────────────────────────────────────────

UDYAM_PATTERN = re.compile(r"UDYAM-[A-Z]{2}-\d{2}-\d{7}", re.IGNORECASE)
GSTIN_PATTERN = re.compile(r"\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}", re.IGNORECASE)
PAN_PATTERN = re.compile(r"[A-Z]{5}\d{4}[A-Z]{1}", re.IGNORECASE)
DATE_PATTERN = re.compile(r"\d{2}[/-]\d{2}[/-]\d{4}")
# Common name/entity patterns from Udyam cert
ENTERPRISE_NAME_PATTERN = re.compile(r"(?:Enterprise Name|Name of Enterprise)[:\s]+([A-Za-z0-9\s&,\.]+)", re.IGNORECASE)
OWNER_NAME_PATTERN = re.compile(r"(?:Owner Name|Name of Owner|Proprietor)[:\s]+([A-Za-z\s]+)", re.IGNORECASE)
NIC_PATTERN = re.compile(r"NIC Code[:\s]*(\d{5})", re.IGNORECASE)


def _extract_text_from_image(image_bytes: bytes) -> str:
    if not OCR_AVAILABLE:
        return ""
    img = Image.open(io.BytesIO(image_bytes))
    # Enhance for OCR
    img = img.convert("L")  # Grayscale
    text = pytesseract.image_to_string(img, lang="eng+hin", config="--psm 6")
    return text


def _extract_text_from_pdf(pdf_bytes: bytes) -> str:
    if not PDF_AVAILABLE:
        return ""
    try:
        pages = convert_from_bytes(pdf_bytes, dpi=200)
        texts = []
        for page in pages[:3]:  # Only first 3 pages
            if OCR_AVAILABLE:
                text = pytesseract.image_to_string(page, lang="eng+hin", config="--psm 6")
                texts.append(text)
        return "\n".join(texts)
    except Exception:
        return ""


def _detect_doc_type(text: str) -> str:
    text_upper = text.upper()
    if "UDYAM" in text_upper or "MINISTRY OF MSME" in text_upper:
        return "udyam_certificate"
    if "GOODS AND SERVICES TAX" in text_upper or "GSTIN" in text_upper:
        return "gst_certificate"
    if "INCOME TAX" in text_upper or "PAN CARD" in text_upper:
        return "pan_card"
    return "unknown_document"


def _parse_document(text: str, doc_type: str) -> dict:
    extracted = {}

    udyam_match = UDYAM_PATTERN.search(text)
    if udyam_match:
        extracted["udyam_number"] = udyam_match.group(0).upper()

    gstin_match = GSTIN_PATTERN.search(text)
    if gstin_match:
        extracted["gstin"] = gstin_match.group(0).upper()

    pan_match = PAN_PATTERN.search(text)
    if pan_match:
        extracted["pan"] = pan_match.group(0).upper()

    dates = DATE_PATTERN.findall(text)
    if dates:
        extracted["registration_date"] = dates[0]

    name_match = ENTERPRISE_NAME_PATTERN.search(text)
    if name_match:
        extracted["enterprise_name"] = name_match.group(1).strip()

    owner_match = OWNER_NAME_PATTERN.search(text)
    if owner_match:
        extracted["owner_name"] = owner_match.group(1).strip()

    nic_match = NIC_PATTERN.search(text)
    if nic_match:
        extracted["nic_activity_code"] = nic_match.group(1)

    return extracted


def _calculate_confidence(extracted: dict, doc_type: str) -> float:
    key_fields = {
        "udyam_certificate": ["udyam_number", "enterprise_name"],
        "gst_certificate": ["gstin"],
        "pan_card": ["pan"],
        "unknown_document": []
    }
    required = key_fields.get(doc_type, [])
    if not required:
        return 0.0
    found = sum(1 for f in required if f in extracted)
    return round(found / len(required), 2)


def _mock_udyam_result() -> dict:
    """Demo result when OCR libraries not installed"""
    return {
        "document_type": "udyam_certificate",
        "extracted_fields": {
            "udyam_number": "UDYAM-UP-01-0001234",
            "enterprise_name": "Agra Leather Works Pvt Ltd",
            "owner_name": "Ramesh Kumar",
            "registration_date": "15/03/2022",
            "nic_activity_code": "15201"
        },
        "verification_status": "verified_demo",
        "confidence": 0.95,
        "raw_text_preview": "(DEMO MODE — install Tesseract OCR for live document scanning)"
    }


def verify_document(file_bytes: bytes, filename: str) -> dict:
    """
    Main entry point. Accepts PDF or image bytes.
    Returns extracted fields and verification status.
    """
    if not OCR_AVAILABLE:
        return _mock_udyam_result()

    filename_lower = filename.lower()
    if filename_lower.endswith(".pdf"):
        text = _extract_text_from_pdf(file_bytes)
    elif filename_lower.endswith((".jpg", ".jpeg", ".png", ".tiff", ".bmp")):
        text = _extract_text_from_image(file_bytes)
    else:
        return {
            "document_type": "unsupported",
            "extracted_fields": {},
            "verification_status": "error",
            "confidence": 0.0,
            "raw_text_preview": "Unsupported file format. Upload PDF or image."
        }

    if not text.strip():
        return {
            "document_type": "unknown_document",
            "extracted_fields": {},
            "verification_status": "unreadable",
            "confidence": 0.0,
            "raw_text_preview": "Could not extract text from document."
        }

    doc_type = _detect_doc_type(text)
    extracted = _parse_document(text, doc_type)
    confidence = _calculate_confidence(extracted, doc_type)

    status = "verified" if confidence >= 0.5 else ("partial" if extracted else "not_verified")

    return {
        "document_type": doc_type,
        "extracted_fields": extracted,
        "verification_status": status,
        "confidence": confidence,
        "raw_text_preview": text[:500].strip()
    }
