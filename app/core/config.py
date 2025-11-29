# External packages
from faster_whisper import WhisperModel

# API lrclib data base
LRCLIB_API = "https://lrclib.net/api/"

# Model Faster whisper
model = WhisperModel("medium", device="cpu", compute_type="float32")
