"""
Groq Voice Service
Uses Groq's ultra-fast Whisper-large-v3 model for Speech-to-Text.
Supports transcription and translation to English.
"""
import os
import io
import asyncio
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

_groq_client = None

def _get_client():
    global _groq_client
    if _groq_client: 
        return _groq_client
    if not GROQ_API_KEY:
        return None
    try:
        from groq import Groq
        _groq_client = Groq(api_key=GROQ_API_KEY)
        return _groq_client
    except Exception as e:
        print(f"[Groq] Init failed: {e}")
        return None


async def transcribe_with_groq(audio_bytes: bytes, filename: str = "audio.wav", task: str = "transcribe", prompt: str = None) -> dict:
    """
    Transcribe audio using Groq Whisper.
    task: 'transcribe' (original lang) or 'translate' (to English)
    """
    client = _get_client()
    if not client:
        return {"error": "GROQ_API_KEY not configured"}

    try:
        def _call_groq():
            if task == "translate":
                return client.audio.translations.create(
                    file=(filename, audio_bytes),
                    model="whisper-large-v3",
                    prompt=prompt,
                    response_format="json",
                    temperature=0.0
                )
            else:
                return client.audio.transcriptions.create(
                    file=(filename, audio_bytes),
                    model="whisper-large-v3",
                    prompt=prompt,
                    response_format="json",
                    temperature=0.0
                )

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, _call_groq)
        
        return {
            "text": response.text,
            "provider": "groq",
            "model": "whisper-large-v3"
        }

    except Exception as e:
        print(f"[Groq] Error: {e}")
        return {"error": str(e)}


async def transcribe_audio_groq(audio_bytes: bytes, source_lang: str = "hi", audio_format: str = "wav") -> dict:
    """
    Returns both original transcript and English translation using Groq.
    Matches Sarvam AI response structure.
    """
    filename = f"audio.{audio_format}"
    
    # Run both transcribe and translate in parallel
    task1 = transcribe_with_groq(audio_bytes, filename, task="transcribe")
    task2 = transcribe_with_groq(audio_bytes, filename, task="translate")
    
    results = await asyncio.gather(task1, task2)
    transcript_res, translate_res = results

    if "error" in transcript_res:
        return transcript_res
    if "error" in translate_res:
        return translate_res

    return {
        "original_transcript": transcript_res["text"],
        "english_translation": translate_res["text"],
        "source_lang": source_lang,
        "provider": "groq",
        "model": "whisper-large-v3"
    }

