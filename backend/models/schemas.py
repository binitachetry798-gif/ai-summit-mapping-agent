from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ─── MSE Onboarding ────────────────────────────────────────────

class MSEOnboardRequest(BaseModel):
    business_name: str = Field(..., example="Agra Leather Works")
    owner_name: str = Field(..., example="Ramesh Kumar")
    phone: Optional[str] = Field(None, example="+91-9876543210")
    location: str = Field(..., example="Agra")
    state: str = Field(..., example="Uttar Pradesh")
    product_description: str = Field(..., example="Handmade leather chappal and sandals")
    annual_capacity: Optional[int] = Field(None, example=1000)
    preferred_language: Optional[str] = Field("en", example="hi")
    udyam_number: Optional[str] = Field(None, example="UDYAM-UP-01-0001234")


class MSEOnboardResponse(BaseModel):
    id: int
    business_name: str
    ondc_category: Optional[str]
    ondc_subcategory: Optional[str]
    hsn_code: Optional[str]
    matched_snp: Optional[dict]
    match_score: Optional[float]
    status: str


# ─── Classification ─────────────────────────────────────────────

class ClassifyRequest(BaseModel):
    description: str = Field(..., example="Handmade silk saree from Varanasi")


class ClassifyResponse(BaseModel):
    category: str
    subcategory: str
    hsn_code: str
    confidence: float
    keywords: List[str]


# ─── SNP Matching ───────────────────────────────────────────────

class SNPMatchRequest(BaseModel):
    product_desc: str = Field(..., example="leather sandal chappal agra")
    location: Optional[str] = Field(None, example="Agra, UP")
    capacity: Optional[int] = Field(None, example=500)
    top_k: Optional[int] = Field(3, example=3)


class SNPMatchResult(BaseModel):
    snp_id: str
    name: str
    domain: str
    sectors: List[str]
    regions: List[str]
    operational_capacity: float
    similarity_score: float
    final_score: float
    contact: Optional[str]
    ondc_id: Optional[str]


class SNPMatchResponse(BaseModel):
    query: str
    matches: List[SNPMatchResult]
    total_snps_evaluated: int


# ─── Voice / Bhashini ───────────────────────────────────────────

class VoiceTranscribeRequest(BaseModel):
    audio_base64: str = Field(..., description="Base64-encoded audio (WAV or MP3)")
    source_lang: str = Field(..., example="hi", description="ISO 639-1 language code")


class VoiceTranscribeResponse(BaseModel):
    original_transcript: str
    english_translation: str
    source_lang: str
    success: bool


# ─── Document Verification ──────────────────────────────────────

class VerifyDocumentResponse(BaseModel):
    document_type: str
    extracted_fields: dict
    verification_status: str
    confidence: float
    raw_text_preview: str
