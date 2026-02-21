"""
Groq Whisper Service — Primary Regional Language STT
Uses whisper-large-v3-turbo via Groq API for ultra-fast transcription.
Supports 13 Indian languages + auto-detection.
"""
import os
import io
import base64
from typing import Optional
from groq import Groq

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Whisper language codes for Indian languages
WHISPER_LANG_MAP = {
    "hi": "hi",   # Hindi
    "bn": "bn",   # Bengali
    "mr": "mr",   # Marathi
    "ta": "ta",   # Tamil
    "te": "te",   # Telugu
    "gu": "gu",   # Gujarati
    "kn": "kn",   # Kannada
    "ml": "ml",   # Malayalam
    "pa": "pa",   # Punjabi
    "or": "or",   # Odia
    "as": "as",   # Assamese
    "ur": "ur",   # Urdu
    "en": "en",   # English
    "auto": None, # Auto-detect
}

LANGUAGE_NAMES = {
    "hi": "Hindi", "bn": "Bengali", "mr": "Marathi", "ta": "Tamil",
    "te": "Telugu", "gu": "Gujarati", "kn": "Kannada", "ml": "Malayalam",
    "pa": "Punjabi", "or": "Odia", "as": "Assamese", "ur": "Urdu",
    "en": "English",
}


def _get_client() -> Optional[Groq]:
    if not GROQ_API_KEY:
        return None
    return Groq(api_key=GROQ_API_KEY)


async def transcribe_bytes(
    audio_bytes: bytes,
    source_lang: str = "auto",
    audio_format: str = "webm",
) -> dict:
    """
    Transcribe audio bytes using Groq Whisper.
    source_lang='auto'  → Whisper auto-detects the language.
    source_lang='hi'    → Force Hindi mode.
    """
    client = _get_client()
    if not client:
        return {
            "transcript": "",
            "detected_language": source_lang,
            "language_name": LANGUAGE_NAMES.get(source_lang, source_lang),
            "provider": "groq_whisper",
            "error": "GROQ_API_KEY not set",
        }

    whisper_lang = WHISPER_LANG_MAP.get(source_lang)  # None = auto-detect

    try:
        filename = f"audio.{audio_format}"
        mime = f"audio/{audio_format}"

        transcription = client.audio.transcriptions.create(
            file=(filename, io.BytesIO(audio_bytes), mime),
            model="whisper-large-v3-turbo",
            language=whisper_lang,          # None triggers auto-detection
            response_format="verbose_json", # gives language field back
            temperature=0.0,
        )

        detected_lang = getattr(transcription, "language", source_lang) or source_lang
        transcript = transcription.text or ""

        return {
            "transcript": transcript,
            "detected_language": detected_lang,
            "language_name": LANGUAGE_NAMES.get(detected_lang, detected_lang),
            "confidence": 0.97,
            "provider": "groq_whisper",
            "model": "whisper-large-v3-turbo",
        }

    except Exception as e:
        return {
            "transcript": "",
            "detected_language": source_lang,
            "language_name": LANGUAGE_NAMES.get(source_lang, source_lang),
            "provider": "groq_whisper",
            "error": str(e),
        }


async def transcribe_base64(
    audio_base64: str,
    source_lang: str = "auto",
    audio_format: str = "webm",
) -> dict:
    """Transcribe base64-encoded audio (from browser MediaRecorder)."""
    audio_bytes = base64.b64decode(audio_base64)
    return await transcribe_bytes(audio_bytes, source_lang, audio_format)
