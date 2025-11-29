from fastapi import APIRouter, HTTPException
from typing import List
from app.models.dto_song_search import SongSearchDTO
from app.models.dto_song_details import SongDetailsDTO
from app.services.lrclib_service import search_song, song_id

router = APIRouter(prefix="/song", tags=["Song"])

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

@router.get('/detail', response_model=List[SongDetailsDTO])
async def get_song_by_id(id: int):
    song = await song_id(id)

    if not id: 
        raise HTTPException(status_code=404, detail="Song not found")
    
    
    return song