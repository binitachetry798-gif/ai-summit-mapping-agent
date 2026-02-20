"""
Sarvam AI Service — Primary Voice Layer
Speech-to-Text + Translation using Sarvam AI APIs (https://api.sarvam.ai)
Supports all major Indian languages with high accuracy.
Docs: https://docs.sarvam.ai
"""
import os
import io
import base64
import httpx
from typing import Optional

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "")
SARVAM_BASE_URL = "https://api.sarvam.ai"

# Language code mapping: our ISO codes → Sarvam language codes
SARVAM_LANG_MAP = {
    "hi": "hi-IN",
    "bn": "bn-IN",
    "mr": "mr-IN",
    "te": "te-IN",
    "ta": "ta-IN",
    "gu": "gu-IN",
    "kn": "kn-IN",
    "ml": "ml-IN",
    "pa": "pa-IN",
    "or": "or-IN",
    "as": "as-IN",
    "ur": "ur-IN",
    "en": "en-IN",
    # Fallbacks
    "mai": "hi-IN",
    "sat": "hi-IN",
    "kok": "mr-IN",
    "doi": "hi-IN",
    "mni": "bn-IN",
    "ks": "ur-IN",
}

SUPPORTED_LANGUAGES = {
    "hi": "Hindi",
    "bn": "Bengali",
    "mr": "Marathi",
    "te": "Telugu",
    "ta": "Tamil",
    "gu": "Gujarati",
    "kn": "Kannada",
    "ml": "Malayalam",
    "pa": "Punjabi",
    "or": "Odia",
    "as": "Assamese",
    "ur": "Urdu",
    "en": "English (Indian)",
}

DEMO_TRANSCRIPTIONS = {
    "hi": "मेरा व्यवसाय हस्तनिर्मित चमड़े के उत्पाद बनाता है, जैसे जूते और बैग। हम आगरा से हैं।",
    "mr": "आम्ही हाताने विणलेल्या रेशीम साड्या बनवतो. आमचा व्यवसाय पुण्यात आहे.",
    "ta": "நாங்கள் கைத்தறி பட்டு புடவைகள் தயாரிக்கிறோம். எங்கள் தொழில் தஞ்சாவூரில் உள்ளது.",
    "te": "మేము చేతితో చేసిన తోలు ఉత్పత్తులు తయారు చేస్తాం. మా వ్యాపారం హైదరాబాద్‌లో ఉంది.",
    "bn": "আমরা হাতে বোনা মসলিন কাপড় তৈরি করি। আমাদের ব্যবসা মুর্শিদাবাদে।",
    "gu": "અમે હસ્તકલા ઉત્પાદનો બનાવીએ છીએ. અમારો ઉદ્યોગ સુરતમાં છે.",
    "kn": "ನಾವು ಕರಕುಶಲ ರೇಶ್ಮೆ ಸೀರೆಗಳನ್ನು ತಯಾರಿಸುತ್ತೇವೆ. ನಮ್ಮ ವ್ಯಾಪಾರ ಮೈಸೂರಿನಲ್ಲಿದೆ.",
    "ml": "ഞങ്ങൾ കൈത്തറി കോട്ടൺ ഉൽപ്പന്നങ്ങൾ നിർമ്മിക്കുന്നു. ഞങ്ങളുടെ ബിസിനസ് കോഴിക്കോട്ടാണ്.",
    "pa": "ਅਸੀਂ ਹੱਥਾਂ ਨਾਲ ਬਣੇ ਫੁਲਕਾਰੀ ਉਤਪਾਦ ਬਣਾਉਂਦੇ ਹਾਂ। ਸਾਡਾ ਕਾਰੋਬਾਰ ਅੰਮ੍ਰਿਤਸਰ ਵਿੱਚ ਹੈ।",
    "or": "ଆମେ ହାତ ବୁଣା ଇକତ ସାଡ଼ି ତିଆରି କରୁ। ଆମ ଉଦ୍ୟୋଗ ସମ୍ବଲପୁରରେ ଅଛି।",
    "en": "We manufacture handmade leather sandals and accessories. Our business is based in Agra, Uttar Pradesh.",
}


async def transcribe_audio(
    audio_bytes: bytes,
    source_lang: str = "hi",
    audio_format: str = "wav",
) -> dict:
    """
    Convert spoken audio in an Indian language to text using Sarvam Speech-to-Text API.
    Falls back to demo response if API key not set.
    """
    if not SARVAM_API_KEY:
        return _demo_response(source_lang)

    sarvam_lang = SARVAM_LANG_MAP.get(source_lang, "hi-IN")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Sarvam expects multipart/form-data with the audio file
            files = {
                "file": (f"audio.{audio_format}", io.BytesIO(audio_bytes), f"audio/{audio_format}"),
            }
            data = {
                "language_code": sarvam_lang,
                "model": "saarika:v2",          # Sarvam's latest ASR model
                "with_timestamps": "false",
                "with_disfluencies": "false",
            }
            headers = {"api-subscription-key": SARVAM_API_KEY}

            response = await client.post(
                f"{SARVAM_BASE_URL}/speech-to-text",
                files=files,
                data=data,
                headers=headers,
            )
            response.raise_for_status()
            result = response.json()

            transcript = result.get("transcript", "")

            # If source is not English, also translate to English
            english_text = transcript
            if source_lang != "en" and transcript:
                english_text = await translate_to_english(transcript, source_lang)

            return {
                "transcript": transcript,
                "english_translation": english_text,
                "language": source_lang,
                "language_name": SUPPORTED_LANGUAGES.get(source_lang, source_lang),
                "confidence": result.get("confidence", 0.95),
                "provider": "sarvam",
                "model": "saarika:v2",
            }

    except httpx.HTTPStatusError as e:
        return {
            "error": f"Sarvam API error: {e.response.status_code} — {e.response.text}",
            "transcript": "",
            "english_translation": "",
            "provider": "sarvam",
        }
    except Exception as e:
        return {
            "error": f"Transcription error: {str(e)}",
            "transcript": "",
            "english_translation": "",
            "provider": "sarvam",
        }


async def transcribe_base64(
    audio_base64: str,
    source_lang: str = "hi",
    audio_format: str = "wav",
) -> dict:
    """Accept base64-encoded audio (from browser MediaRecorder)."""
    audio_bytes = base64.b64decode(audio_base64)
    return await transcribe_audio(audio_bytes, source_lang, audio_format)


async def translate_to_english(text: str, source_lang: str) -> str:
    """Translate Indian language text to English using Sarvam Translate API."""
    if not SARVAM_API_KEY or source_lang == "en":
        return text

    sarvam_lang = SARVAM_LANG_MAP.get(source_lang, "hi-IN")

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            headers = {
                "api-subscription-key": SARVAM_API_KEY,
                "Content-Type": "application/json",
            }
            payload = {
                "input": text,
                "source_language_code": sarvam_lang,
                "target_language_code": "en-IN",
                "speaker_gender": "Male",
                "mode": "formal",
                "model": "mayura:v1",
                "enable_preprocessing": True,
            }
            response = await client.post(
                f"{SARVAM_BASE_URL}/translate",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            result = response.json()
            return result.get("translated_text", text)

    except Exception:
        return text  # Return original on error


async def text_to_speech(text: str, target_lang: str = "hi") -> Optional[bytes]:
    """Convert text to speech in target Indian language using Sarvam TTS."""
    if not SARVAM_API_KEY:
        return None

    sarvam_lang = SARVAM_LANG_MAP.get(target_lang, "hi-IN")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {
                "api-subscription-key": SARVAM_API_KEY,
                "Content-Type": "application/json",
            }
            payload = {
                "inputs": [text[:500]],          # Max 500 chars per request
                "target_language_code": sarvam_lang,
                "speaker": "meera",              # Sarvam's Hindi/multilingual speaker
                "pitch": 0,
                "pace": 1.0,
                "loudness": 1.5,
                "speech_sample_rate": 8000,
                "enable_preprocessing": True,
                "model": "bulbul:v1",
            }
            response = await client.post(
                f"{SARVAM_BASE_URL}/text-to-speech",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            result = response.json()
            audios = result.get("audios", [])
            if audios:
                return base64.b64decode(audios[0])
            return None
    except Exception:
        return None


def get_supported_languages() -> dict:
    return SUPPORTED_LANGUAGES


def _demo_response(source_lang: str) -> dict:
    """Return realistic demo transcription when no API key is set."""
    transcript = DEMO_TRANSCRIPTIONS.get(source_lang, DEMO_TRANSCRIPTIONS["hi"])
    english = DEMO_TRANSCRIPTIONS["en"]
    return {
        "transcript": transcript,
        "english_translation": english,
        "language": source_lang,
        "language_name": SUPPORTED_LANGUAGES.get(source_lang, source_lang),
        "confidence": 0.97,
        "provider": "sarvam_demo",
        "note": "DEMO MODE — Set SARVAM_API_KEY in .env for live transcription",
    }
