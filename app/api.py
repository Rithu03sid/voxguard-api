from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
import base64, os, time, binascii

from core.audio_processing import load_audio
from core.feature_extraction import extract_features
from core.predict import predict_voice
from core.language_detection import detect_language

router = APIRouter()

API_KEY = os.getenv("VOXGUARD_API_KEY", "VOXGUARD_SECURE_KEY_2026")

class AudioRequest(BaseModel):
    audio_base64: str

@router.get("/health")
def health():
    return {"status": "ok"}

@router.post("/detect")
def detect_voice(
    req: AudioRequest,
    x_api_key: str = Header(..., alias="x-api-key")
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    start_time = time.time()

    try:
        audio_bytes = base64.b64decode(req.audio_base64, validate=True)
    except (binascii.Error, ValueError):
        raise HTTPException(status_code=400, detail="Invalid Base64 audio")

    temp_path = "temp.mp3"
    with open(temp_path, "wb") as f:
        f.write(audio_bytes)

    audio = load_audio(temp_path)
    features = extract_features(audio, 16000)

    classification, confidence = predict_voice(features)
    language = detect_language(audio)

    try:
        os.remove(temp_path)
    except OSError:
        pass

    processing_time = round(time.time() - start_time, 3)

    return {
        "status": "success",
        "language": language,
        "classification": classification,
        "confidence": f"{confidence}%",
        "processing_time": f"{processing_time} seconds"
    }
