from app.core.config import LRCLIB_API
from app.core.http_client import async_client
from app.core.models.songs import Song, SongTranslation
from sqlalchemy.orm import Session
from typing import Optional
from app.models.dto_song_details import SongDetailsDTO
from app.models.dto_song_search import SongSearchDTO



async def search_song(q: str = None, track_name: str = None, artist_name: str = None, album_name: str = None) -> list[SongSearchDTO]:

    params = {
        "q": q,
        "track_name": track_name,
        "artist_name": artist_name,
        "album_name": album_name
    }

    resp = await async_client.get(LRCLIB_API + "search", params=params)
    resp.raise_for_status()

    data = resp.json()

    if not isinstance(data, list):
        return []

    return [SongSearchDTO(**item) for item in data]

async def song_id(id: int, db: Session) -> Optional[SongDetailsDTO]:
    
    song = db.query(Song).filter(Song.id == id).first()
    if song:
        translation = db.query(SongTranslation).filter(
            SongTranslation.song_id == id, 
            SongTranslation.target_language == "ru"
        ).first()
        
        return SongDetailsDTO(
            id=song.id,
            trackName=song.track_name,
            artistName=song.artist_name,
            plainLyrics=song.lyrics,
            translation=translation.translation if translation else None,
            translationStatus=translation.status if translation else None
        )
    
    try:
        response = await async_client.get(f"{LRCLIB_API}get/{id}")
        response.raise_for_status()
        data = response.json()
        
        if not isinstance(data, dict):
            return None
        
        db_song = Song(
            id=data["id"],
            track_name=data["trackName"],
            artist_name=data["artistName"],
            lyrics=data["plainLyrics"],
            language="de"  # change later
        )
        db.add(db_song)
        db.commit()
        db.refresh(db_song)  
        
        return SongDetailsDTO(**data)
        
    except Exception as e:
        print(f"LRCLIB error: {e}")
        return None