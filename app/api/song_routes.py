from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session  # ← Правильный импорт!
from app.core.database.database import get_db  # ← Правильный путь!
from app.models.dto_song_search import SongSearchDTO
from app.models.dto_song_details import SongDetailsDTO
from app.services.lrclib_service import search_song, song_id
from app.core.models.songs import Song, SongTranslation
from app.services.perplexity_service import translate_song_lyrics  # ← Импорты для song_id

router = APIRouter(prefix="/song", tags=["Song"])

# -------------------- 
# -     SEARCH       -
# --------------------

@router.get("/search", response_model=List[SongSearchDTO])
async def get_song_from_lrclib(
    q: str = None,
    track_name: str = None,
    artist_name: str = None,
    album_name: str = None
):
    if not any([q, track_name, artist_name, album_name]):
        return []
    return await search_song(q, track_name, artist_name, album_name)


# ----------------------- 
# -     SONG BY ID      -
# -----------------------

@router.get('/detail', response_model=SongDetailsDTO)  # ← Убрал List!
async def get_song_by_id(id: int, db: Session = Depends(get_db)):
    song = await song_id(id, db)  # ← ПЕРЕДАЛ db!
    
    if not song:  # ← ПРОВЕРЯЕМ song, не id!
        raise HTTPException(status_code=404, detail="Song not found")
    
    return song  # ← Возвращаем объект, не список!


# ------------------------
# -     TRANSLATION      -
# ------------------------


@router.post("/detail/{id}/translate")
async def translate_song(id: int, db: Session = Depends(get_db)):
    song = db.query(Song).filter(Song.id == id).first()

    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    
    existing_translation = db.query(SongTranslation).filter(
        SongTranslation.song_id == id,
        SongTranslation.target_language == 'ru'
    ).first()

    if existing_translation and existing_translation.status == 'reafy':
        return {
            "songId": id,
            "translation": existing_translation.translation,
            "status": "ready"
        }
    
    translation_text = await translate_song_lyrics(song.lyrics)
    
    if translation_text:
        if existing_translation:
            existing_translation.translation = translation_text
            existing_translation.status = 'ready'
        else:
            translation = SongTranslation(
                song_id=id,
                source_language="de",
                target_language="ru",
                translation=translation_text,
                status="ready"
            )
            db.add(translation)
        
        db.commit()
        return {
            "songId": id,
            "translation": translation_text,
            "status": "ready"
        }
    else: 
        if existing_translation:
            existing_translation.status = "unavailable"
        else:
            translation = SongTranslation(
            song_id=id,
                source_language="de",
                target_language="ru",
                translation=translation_text,
                status="unavailable"
            )
            db.add(translation)
            db.commit()

        return {
            "songId": id,
            "translate": None,
            "status": "unavailable"
        }




    