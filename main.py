from fastapi import FastAPI, UploadFile, File, HTTPException
from faster_whisper import WhisperModel
from io import BytesIO
import tempfile  
import httpx

from fastapi.middleware.cors import CORSMiddleware



# DI | Fastapi call
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# DI | whisper model dependency params for pc
model = WhisperModel("medium", device="cpu", compute_type="float32")


# |untitled Just root message to ping endpoint
@app.get('/')
def read_root():
    return {'message': 'hello world!' }


# DI API | LRCLIB API call for search the song
LRCLIB_API = 'https://lrclib.net/api/'






@app.get("/song")
async def get_song_from_lrclib(q: str = None, track_name: str = None, artist_name: str = None):
    if not q and not track_name:
        return {"success": False, "error": "You must provide at least 'q' or 'track_name'", "data": []}

    params = {
        "q": q,
        "track_name": track_name,
        "artist_name": artist_name
    }

    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.get(LRCLIB_API + "search", params=params)
            resp.raise_for_status()

            data = resp.json()

            # 📌 LRCLIB возвращает список → отдать как есть
            if isinstance(data, list):
                return {"success": True, "data": data}

            # 📌 если вдруг вернет словарь (на будущее)
            if isinstance(data, dict) and "results" in data:
                return {"success": True, "data": data["results"]}

            return {"success": True, "data": []}

        except httpx.ReadTimeout:
            return {"success": False, "error": "LRCLIB timeout", "data": []}
        except httpx.HTTPStatusError as e:
            return {"success": False, "error": f"LRCLIB status error: {e.response.status_code}", "data": []}
        except Exception as e:
            return {"success": False, "error": str(e), "data": []}

# #2 GET | Get LIST of searched songs RESULT


# #3 GET | Get selected song from LRCLIB Data Base 
# ?? get_cached endpoint / get_by_id
@app.get('/song/id')
async def get_song_by_id(id: int = None):
    if not id: 
        raise HTTPException(
            status_code=400,
            detail="You should choise the track id"
        )
    params = {"id": id}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get('${LRCLIB_API}', params=params)
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=str(e))
    
    return data

# #4 TRANSCRIBE | IF the user cannot find the exact song that he search 
# Whisper transcription for last fall in order
@app.post("/transcribe")
async def transcription(file: UploadFile = File(...)):
    audio_bytes = await file.read()
    with tempfile.NamedTemporaryFile(suffix=".mp3") as temp_file:
        temp_file.write(audio_bytes)
        temp_file.flush()

        segments, info = model.transcribe(temp_file.name, language='ja', beam_size=10)

    text = ""
    for segment in segments:
        text += segment.text + " "

    return {"text": text.strip()}


# ------------------------------------------------------------------------
# Lyrics manipulation
# ENPOINTS:
# 1 TRANSLATE THE SONG LYRICS
# 2 GET ONE WORD RANDOMLY FROM LYRICS 
# 3 GIVE AN TRANSLATE TO A WORD
# 4 SORT WORD CARDS TO KNOWN OR UNKNOWN | STATUS




# ??? i should confirm the UPLOAD FILE from USER, SEARCH the ARTIST & SONG and return the json text
# !!! the're much easiest way, let's give to te USER opportunity as INPUT where he can SEARCH the musik songs by himself
# in that way i need to have DATA BASE to make a requests IF song are EXIST in your BASE and searching algorithm
# 
# ^!!! Most easiest way is user upload the text itself as file to the app, and algorithm makes this text as cards to learn and gives to user as a lektion[N]  
#   
#
# then i should transform this json text to a List with this properties 
# {
# textRandom word : 'word'
# etc...
# }
# like i return the RANDOM WORDS to the USER as a card to memorise it, 
# and at the end that is one whole SESSION[n] with title of the name this SONG with words inside it ~30-100
# 
#
# EXMAPLE of user_card_progress 
# | user_id | song_id | word | status | repetitions | easiness | next_review |
# |----------|----------|----------|-------------|--------------|------------|
# | 1 | 12345 | 青い | known | 3 | 2.7 | 2025-11-10 |
# | 1 | 12345 | 空 | learning | 1 | 2.3 | 2025-11-08 |
# 
# 
# 
# 
# 
# 
# 
# 
#
#
# 
# 
# 
# 
# 
# 
# 
# 
# 
#  

