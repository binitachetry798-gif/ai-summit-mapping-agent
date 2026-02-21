"""
Voice Router — Speech-to-Text + Translation
Primary:  Groq Whisper (whisper-large-v3-turbo) — ultra-fast, auto language detect
Fallback: Sarvam AI (saarika:v2) — Indian language specialist
"""
from fastapi import APIRouter, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional
from services.groq_whisper import transcribe_base64 as groq_transcribe_base64
from services.sarvam import (
    transcribe_base64 as sarvam_transcribe_base64,
    translate_to_english,
    text_to_speech,
    get_supported_languages,
)

router = APIRouter(prefix="/voice", tags=["Voice & Language"])


class TranscribeBase64Request(BaseModel):
    audio_base64: str
    source_lang: str = "auto"   # 'auto' = Groq auto-detects, or pass 'hi','ta','te' etc.
    audio_format: str = "webm"


class TranslateRequest(BaseModel):
    text: str
    source_lang: str = "hi"


class TTSRequest(BaseModel):
    text: str
    target_lang: str = "hi"


@router.get("/languages", summary="List all supported Indian languages")
async def get_languages():
    """Returns all 13 supported Indian languages with ISO codes."""
    langs = get_supported_languages()
    return {
        "languages": langs,
        "total": len(langs),
        "primary_provider": "Groq Whisper (whisper-large-v3-turbo)",
        "fallback_provider": "Sarvam AI (saarika:v2)",
        "auto_detect": True,
        "note": "Use source_lang='auto' for automatic language detection",
    }


@router.post("/transcribe/base64", summary="🎙️ Transcribe regional audio (Groq Whisper + Sarvam fallback)")
async def transcribe_voice_base64(request: TranscribeBase64Request):
    """
    Transcribe base64-encoded browser audio in any Indian language.

    - **source_lang=auto** → Groq Whisper auto-detects language
    - **source_lang=hi/ta/te/kn/...** → Force specific language
    - Falls back to Sarvam AI if Groq fails

    Returns: transcript (regional) + english_translation + detected_language
    """
    # Primary: Groq Whisper
    result = await groq_transcribe_base64(
        audio_base64=request.audio_base64,
        source_lang=request.source_lang,
        audio_format=request.audio_format,
    )

    # Fallback to Sarvam if Groq fails or returns empty
    if result.get("error") or not result.get("transcript"):
        lang = request.source_lang if request.source_lang != "auto" else "hi"
        sarvam_result = await sarvam_transcribe_base64(
            audio_base64=request.audio_base64,
            source_lang=lang,
            audio_format=request.audio_format,
        )
        if sarvam_result.get("transcript"):
            return sarvam_result

    # If Groq succeeded, add English translation for non-English
    transcript = result.get("transcript", "")
    detected_lang = result.get("detected_language", "hi")

    english_text = transcript
    if detected_lang not in ("en", "english") and transcript:
        english_text = await translate_to_english(transcript, detected_lang[:2])

    return {
        **result,
        "english_translation": english_text,
    }


@router.post("/transcribe", summary="Transcribe audio file upload (multipart)")
async def transcribe_voice_file(
    file: UploadFile = File(...),
    source_lang: str = Form("auto"),
):
    """Transcribe uploaded audio file (wav/mp3/webm/ogg)."""
    import base64
    audio_bytes = await file.read()
    audio_b64 = base64.b64encode(audio_bytes).decode()
    fmt = (file.filename or "audio.webm").rsplit(".", 1)[-1]

    result = await groq_transcribe_base64(audio_b64, source_lang, fmt)
    transcript = result.get("transcript", "")
    detected_lang = result.get("detected_language", "hi")

    english_text = transcript
    if detected_lang not in ("en", "english") and transcript:
        english_text = await translate_to_english(transcript, detected_lang[:2])

    return {**result, "english_translation": english_text}


@router.post("/translate", summary="Translate Indian language text to English")
async def translate_text(request: TranslateRequest):
    """Translate regional language text to English using Sarvam Translate."""
    translated = await translate_to_english(request.text, request.source_lang)
    return {
        "original": request.text,
        "translated": translated,
        "source_lang": request.source_lang,
    }


@router.post("/tts", summary="Text-to-Speech in Indian language (Sarvam bulbul:v1)")
async def text_to_speech_endpoint(request: TTSRequest):
    """Convert text to speech in target Indian language."""
    import base64
    audio_bytes = await text_to_speech(request.text, request.target_lang)
    if not audio_bytes:
        return {"error": "TTS unavailable. Set SARVAM_API_KEY.", "audio_base64": None}
    return {
        "audio_base64": base64.b64encode(audio_bytes).decode(),
        "target_lang": request.target_lang,
        "format": "wav",
    }
