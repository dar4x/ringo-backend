import httpx
import tempfile  
from faster_whisper import WhisperModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, File, HTTPException

from app.api.song_routes import router as song_router
from app.services.lrclib_service import LRCLIB_API

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(song_router)

model = WhisperModel("medium", device="cpu", compute_type="float32")


@app.get("/")
def read_root():
    return {"message": "hello world!"}


@app.get('/song/id')
async def get_song_by_id(id: int = None):
    if not id:
        raise HTTPException(
            status_code=400,
            detail="You should choose the track id"
        )

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{LRCLIB_API}get/{id}")
            resp.raise_for_status()
            return resp.json()

        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=str(e))


@app.post("/transcribe")
async def transcription(file: UploadFile = File(...)):
    audio_bytes = await file.read()

    with tempfile.NamedTemporaryFile(suffix=".mp3") as temp_file:
        temp_file.write(audio_bytes)
        temp_file.flush()

        segments, info = model.transcribe(
            temp_file.name,
            language='ja',
            beam_size=10
        )

    text = " ".join([s.text for s in segments])
    return {"text": text}
