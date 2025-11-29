# Internal packages
from app.models.dto_song_search import SongSearchDTO
from app.models.dto_song_details import SongDetailsDTO
from app.core.config import LRCLIB_API
from app.core.http_client import async_client



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

async def song_id(id: int = None) -> SongDetailsDTO | None:

    response = await async_client.get(f"{LRCLIB_API}get/{id}")
    response.raise_for_status()

    data = response.json()

    if not isinstance(data, dict):
        return None
        
    return [
        SongDetailsDTO(**data)
    ]
        