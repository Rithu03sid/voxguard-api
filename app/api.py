from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import base64
import os
import time

from core.audio_processing import load_audio
from core.feature_extraction import extract_features
from core.predict import predict_voice
from core.language_detection import detect_language

# ----------------------------
# CONFIG
# ----------------------------
API_KEY = "VOXGUARD_SECURE_KEY_2026"
TEMP_AUDIO_FILE = "temp_audio.mp3"

router = APIRouter()

# ----------------------------
# REQUEST MODEL
# Accepts BOTH camelCase & snake_case
# ----------------------------
class AudioRequest(BaseModel):
    language: Optional[str] = None

    # Accepts audioFormat or audio_format
    audio_format: Optional[str] = Field(None, alias="audioFormat")

    # Accepts audioBase64 or audio_base64
    audio_base64: str = Field(..., alias="audioBase64")

    class Config:
        allow_population_by_field_name = True


# ----------------------------
# API ENDPOINT
# ----------------------------
@router.post("/detect")
def detect_voice(
    request: AudioRequest,
    x_api_key: str = Header(...)
):
    # 🔐 API KEY VALIDATION
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    start_time = time.time()

    # ----------------------------
    # Decode Base64 → MP3
    # ----------------------------
    try:
        audio_bytes = base64.b64decode(request.audio_base64)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid Base64 audio")

    with open(TEMP_AUDIO_FILE, "wb") as f:
        f.write(audio_bytes)

    # ----------------------------
    # Audio Processing
    # ----------------------------
    try:
        audio = load_audio(TEMP_AUDIO_FILE)
        features = extract_features(audio, 16000)
        classification, confidence = predict_voice(features)

        # Detect language from audio
        detected_language = detect_language(audio)

    finally:
        if os.path.exists(TEMP_AUDIO_FILE):
            os.remove(TEMP_AUDIO_FILE)

    processing_time = round(time.time() - start_time, 3)

    # ----------------------------
    # FINAL JSON RESPONSE
    # ----------------------------
    return {
        "status": "success",
        "language": detected_language,
        "classification": classification,
        "confidence": f"{confidence}%",
        "processing_time": f"{processing_time} seconds"
    }

