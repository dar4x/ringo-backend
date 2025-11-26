import httpx
from app.models.dto_song_search import SongDetailsDTO

LRCLIB_API = "https://lrclib.net/api/"

async def search_song(q: str = None, track_name: str = None, artist_name: str = None, album_name: str = None) -> list[SongDetailsDTO]:

    params = {
        "q": q,
        "track_name": track_name,
        "artist_name": artist_name,
        "album_name": album_name
    }

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(LRCLIB_API + "search", params=params)
        resp.raise_for_status()

        data = resp.json()

        if not isinstance(data, list):
            return []

        return [
            SongDetailsDTO(
                id=item.get("id"),
                trackName=item.get("trackName"),
                artistName=item.get("artistName"),
                albumName=item.get('albumName')
            )
            for item in data
        ]
