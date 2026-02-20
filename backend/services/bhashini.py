"""
Bhashini ULCA Integration Service
Handles Speech-to-Text (ASR) + Machine Translation (NMT) pipeline.
Reference: https://bhashini.gov.in/ulca
"""
import os
import requests
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

BHASHINI_USER_ID = os.getenv("BHASHINI_USER_ID", "")
BHASHINI_API_KEY = os.getenv("BHASHINI_API_KEY", "")
BHASHINI_PIPELINE_ID = os.getenv("BHASHINI_PIPELINE_ID", "64392f96daac500b55c543cd")

PIPELINE_CONFIG_URL = "https://meity-auth.ulcacontrib.org/ulca/apis/v0/model/getModelsPipeline"
INFERENCE_URL = "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"

# Supported language codes (ISO 639-1 / Bhashini codes)
SUPPORTED_LANGUAGES = {
    "hi": "Hindi", "bn": "Bengali", "mr": "Marathi",
    "te": "Telugu", "ta": "Tamil", "gu": "Gujarati",
    "ur": "Urdu", "kn": "Kannada", "or": "Odia",
    "ml": "Malayalam", "pa": "Punjabi", "as": "Assamese",
    "mai": "Maithili", "sat": "Santali", "ks": "Kashmiri",
    "kok": "Konkani", "doi": "Dogri", "mni": "Manipuri",
    "en": "English", "sa": "Sanskrit"
}


def _is_configured() -> bool:
    return bool(BHASHINI_USER_ID and BHASHINI_API_KEY
                and BHASHINI_USER_ID != "your_bhashini_user_id"
                and BHASHINI_API_KEY != "your_bhashini_ulca_api_key")


def _get_pipeline_config(source_lang: str, target_lang: str = "en") -> Optional[dict]:
    """Fetch dynamic pipeline config from Bhashini ULCA."""
    payload = {
        "pipelineTasks": [
            {"taskType": "asr", "config": {"language": {"sourceLanguage": source_lang}}},
            {"taskType": "translation", "config": {
                "language": {"sourceLanguage": source_lang, "targetLanguage": target_lang}
            }}
        ],
        "pipelineRequestConfig": {"pipelineId": BHASHINI_PIPELINE_ID}
    }
    headers = {
        "Content-Type": "application/json",
        "userID": BHASHINI_USER_ID,
        "ulcaApiKey": BHASHINI_API_KEY
    }
    try:
        resp = requests.post(PIPELINE_CONFIG_URL, json=payload, headers=headers, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return None


def _run_inference(config_response: dict, audio_base64: str) -> Optional[dict]:
    """Run the actual ASR + NMT inference via Bhashini."""
    try:
        endpoint = config_response["pipelineInferenceAPIEndPoint"]
        callback_url = endpoint["callbackUrl"]
        key_name = endpoint["inferenceApiKey"]["name"]
        key_val = endpoint["inferenceApiKey"]["value"]

        pipeline_tasks = []
        for i, task_config in enumerate(config_response["pipelineResponseConfig"]):
            task_type = task_config["taskType"]
            model_config = task_config["config"][0]
            pipeline_tasks.append({"taskType": task_type, "config": model_config})

        compute_payload = {
            "pipelineTasks": pipeline_tasks,
            "inputData": {"audio": [{"audioContent": audio_base64}]}
        }

        headers = {key_name: key_val, "Content-Type": "application/json"}
        result = requests.post(callback_url, json=compute_payload, headers=headers, timeout=30)
        result.raise_for_status()
        return result.json()
    except Exception as e:
        return None


def _extract_results(inference_result: dict) -> tuple[str, str]:
    """Extract transcript and translation from Bhashini pipeline response."""
    transcript = ""
    translation = ""
    try:
        for task in inference_result.get("pipelineResponse", []):
            if task.get("taskType") == "asr":
                outputs = task.get("output", [])
                if outputs:
                    transcript = outputs[0].get("source", "")
            elif task.get("taskType") == "translation":
                outputs = task.get("output", [])
                if outputs:
                    translation = outputs[0].get("target", "")
    except Exception:
        pass
    return transcript, translation


def _mock_transcription(source_lang: str) -> tuple[str, str]:
    """
    Mock transcription when Bhashini API is not configured.
    Returns a demo result for development/testing.
    """
    demo_transcripts = {
        "hi": ("मैं हस्तनिर्मित चमड़े की चप्पल बनाता हूं", "I make handmade leather chappal"),
        "mr": ("मी हाताने विणलेल्या रेशमी साड्या बनवतो", "I make hand-woven silk sarees"),
        "ta": ("நான் கைத்தறி ஆடைகள் தயாரிக்கிறேன்", "I manufacture handloom garments"),
        "bn": ("আমি হাতে তৈরি মাটির পাত্র বানাই", "I make handmade earthen pots"),
        "gu": ("હું ઓર્ગેનિક મસાલા અને અથાણું બનાવું છું", "I make organic spices and pickles"),
        "kn": ("ನಾನು ಕರಕುಶಲ ಬಿದಿರಿನ ಉತ್ಪನ್ನಗಳನ್ನು ತಯಾರಿಸುತ್ತೇನೆ", "I manufacture handcraft bamboo products"),
    }
    return demo_transcripts.get(source_lang, (
        "(Demo: audio not processed — Bhashini key not configured)",
        "Handmade traditional craft product from local artisan"
    ))


def transcribe_and_translate(audio_base64: str, source_lang: str) -> dict:
    """
    Main entry point. Transcribes audio and translates to English.
    Uses Bhashini if configured, otherwise returns mock demo data.
    """
    if source_lang not in SUPPORTED_LANGUAGES:
        return {
            "success": False,
            "original_transcript": "",
            "english_translation": "",
            "source_lang": source_lang,
            "error": f"Unsupported language: {source_lang}. Supported: {list(SUPPORTED_LANGUAGES.keys())}"
        }

    # If English, skip translation
    if source_lang == "en":
        # In real usage, still run ASR
        return {
            "success": True,
            "original_transcript": "(English audio — ASR result)",
            "english_translation": "(English audio — no translation needed)",
            "source_lang": source_lang
        }

    if not _is_configured():
        transcript, translation = _mock_transcription(source_lang)
        return {
            "success": True,
            "original_transcript": transcript,
            "english_translation": translation,
            "source_lang": source_lang,
            "note": "DEMO MODE — configure BHASHINI_API_KEY in .env for live transcription"
        }

    # Live Bhashini pipeline
    config = _get_pipeline_config(source_lang)
    if config is None:
        return {"success": False, "original_transcript": "", "english_translation": "",
                "source_lang": source_lang, "error": "Failed to fetch Bhashini pipeline config"}

    result = _run_inference(config, audio_base64)
    if result is None:
        return {"success": False, "original_transcript": "", "english_translation": "",
                "source_lang": source_lang, "error": "Bhashini inference failed"}

    transcript, translation = _extract_results(result)
    return {
        "success": True,
        "original_transcript": transcript,
        "english_translation": translation,
        "source_lang": source_lang
    }
