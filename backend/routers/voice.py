"""
Voice Router — Speech-to-Text + Translation
Primary: Sarvam AI (saarika:v2 ASR + mayura:v1 NMT)
Fallback: Demo mode (realistic mock responses)
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional
from services.sarvam import (
    transcribe_audio,
    transcribe_base64,
    translate_to_english,
    text_to_speech,
    get_supported_languages,
    SARVAM_API_KEY,
)

from services.groq_service import GROQ_API_KEY, transcribe_audio_groq

router = APIRouter(prefix="/voice", tags=["voice"])


class TranscribeBase64Request(BaseModel):
    audio_base64: str
    source_lang: str = "hi"
    audio_format: str = "wav"


class TranslateRequest(BaseModel):
    text: str
    source_lang: str = "hi"


class TTSRequest(BaseModel):
    text: str
    target_lang: str = "hi"


@router.get("/languages")
async def get_languages():
    """List all supported Indian languages with ISO codes."""
    langs = get_supported_languages()
    
    provider = "Sarvam AI"
    models = {
        "asr": "saarika:v2",
        "translation": "mayura:v1",
        "tts": "bulbul:v1"
    }
    
    if GROQ_API_KEY:
        provider = "Groq (Whisper)"
        models["asr"] = "whisper-large-v3"
        # Translation still mayura:v1 for text-to-text, 
        # but Whisper handles audio-to-text translation

    return {
        "provider": provider,
        "models": models,
        "api_key_configured": bool(SARVAM_API_KEY or GROQ_API_KEY),
        "total": len(langs),
        "languages": [
            {"code": code, "name": name}
            for code, name in langs.items()
        ]
    }


@router.get("/status")
async def voice_status():
    """Check API connectivity status."""
    return {
        "providers": {
            "sarvam": {"active": bool(SARVAM_API_KEY), "role": "TTS + Translate + Backup ASR"},
            "groq": {"active": bool(GROQ_API_KEY), "role": "Primary ASR (Whisper)"}
        },
        "mode": "live" if (SARVAM_API_KEY or GROQ_API_KEY) else "demo",
        "primary_asr": "groq" if GROQ_API_KEY else "sarvam" if SARVAM_API_KEY else "demo",
        "endpoints": {
            "speech_to_text": "/voice/transcribe",
            "transcribe_base64": "/voice/transcribe/base64",
            "translate": "/voice/translate",
            "text_to_speech": "/voice/tts",
        }
    }


@router.post("/transcribe")
async def transcribe_voice(
    file: UploadFile = File(...),
    source_lang: str = Form("hi"),
):
    """
    Upload an audio file and transcribe it.
    Uses Groq Whisper-large-v3 if available, else Sarvam.
    """
    audio_bytes = await file.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio file")

    # Detect format from filename
    fname = (file.filename or "audio.wav").lower()
    fmt = "wav"
    for ext in ["mp3", "ogg", "webm", "m4a", "flac", "wav"]:
        if fname.endswith(ext):
            fmt = ext
            break

    # Prioritize Groq for ASR
    if GROQ_API_KEY:
        try:
            result = await transcribe_audio_groq(audio_bytes, source_lang, audio_format=fmt)
            if "error" not in result:
                return result
            print(f"[Voice] Groq failed, falling back to Sarvam: {result['error']}")
        except Exception as e:
            print(f"[Voice] Groq error: {e}")

    # Fallback to Sarvam
    result = await transcribe_audio(audio_bytes, source_lang=source_lang, audio_format=fmt)

    if "error" in result:
        raise HTTPException(status_code=502, detail=result["error"])

    return result


@router.post("/transcribe/base64")
async def transcribe_voice_base64(request: TranscribeBase64Request):
    """
    Transcribe base64-encoded audio.
    Uses Groq Whisper-large-v3 if available, else Sarvam.
    """
    if not request.audio_base64:
        raise HTTPException(status_code=400, detail="No audio data provided")

    # Decode base64 to bytes
    import base64
    try:
        audio_bytes = base64.b64decode(request.audio_base64)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 string")

    # Prioritize Groq for ASR
    if GROQ_API_KEY:
        try:
            result = await transcribe_audio_groq(
                audio_bytes, 
                request.source_lang, 
                audio_format=request.audio_format
            )
            if "error" not in result:
                return result
            print(f"[Voice] Groq failed, falling back to Sarvam: {result['error']}")
        except Exception as e:
            print(f"[Voice] Groq error: {e}")

    # Fallback to Sarvam
    result = await transcribe_base64(
        request.audio_base64,
        source_lang=request.source_lang,
        audio_format=request.audio_format,
    )

    if "error" in result:
        raise HTTPException(status_code=502, detail=result["error"])

    return result


@router.post("/translate")
async def translate_text(request: TranslateRequest):
    """
    Translate Indian language text to English using Sarvam mayura:v1.
    """
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    english = await translate_to_english(request.text, request.source_lang)
    return {
        "original": request.text,
        "english_translation": english,
        "source_lang": request.source_lang,
        "provider": "sarvam",
        # ... rest remains handled by Sarvam for text-to-text

        "model": "mayura:v1",
    }


@router.post("/tts")
async def synthesize_speech(request: TTSRequest):
    """
    Convert text to speech in target Indian language using Sarvam bulbul:v1.
    Returns base64-encoded WAV audio.
    """
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    if not SARVAM_API_KEY:
        return {
            "audio_base64": None,
            "message": "TTS requires SARVAM_API_KEY — set it in backend/.env",
            "provider": "sarvam_demo",
        }

    audio_bytes = await text_to_speech(request.text, request.target_lang)
    if not audio_bytes:
        raise HTTPException(status_code=502, detail="TTS generation failed")

    import base64
    return {
        "audio_base64": base64.b64encode(audio_bytes).decode(),
        "target_lang": request.target_lang,
        "provider": "sarvam",
        "model": "bulbul:v1",
    }
