from fastapi import APIRouter
from typing import List
from app.models.dto_song_search import SongDetailsDTO
from app.services.lrclib_service import search_song

router = APIRouter(prefix="/song", tags=["Song"])

@router.get("/search", response_model=List[SongDetailsDTO])
async def get_song_from_lrclib(
    q: str = None,
    track_name: str = None,
    artist_name: str = None
):
    if not any([q, track_name, artist_name]):
        return []

    return await search_song(q, track_name, artist_name)
