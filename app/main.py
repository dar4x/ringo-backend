# External packages
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

# Internal packages
from app.api.song_routes import router as song_router
from app.core.database.database import DATABASE_URL, engine, SessionLocal, get_db, Base
from app.core.models.songs import Song, SongTranslation


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(song_router)


@app.get("/")
def read_root():
    return {"message": "hello world!"}
@app.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table';")).fetchall()
        return {
            "status": "DB connected!", 
            "engine": "sqlite:///./song_learner.db",  # ← Жёстко прописали
            "tables": [row[0] for row in result]
        }
    except Exception as e:
        return {"status": "DB error", "error": str(e)}


@app.get("/test-perplexity")
async def test_perplexity():
    from app.core.config import PERPLEXITY_API_KEY
    return {
        "key_exists": bool(PERPLEXITY_API_KEY),
        "key_preview": PERPLEXITY_API_KEY[:20] + "..." if PERPLEXITY_API_KEY else None
    }