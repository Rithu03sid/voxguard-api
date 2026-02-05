import librosa
def detect_language(audio, sr=16000):
    pitch = librosa.yin(audio, fmin=50, fmax=300)
    avg = float(pitch.mean())
    if avg < 130:
        return "Tamil / Malayalam"
    elif avg < 160:
        return "Telugu"
    elif avg < 190:
        return "Hindi"
    else:
        return "English"
