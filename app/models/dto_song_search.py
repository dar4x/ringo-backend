from pydantic import BaseModel

class SongSearchDTO(BaseModel):
    id: int
    trackName: str
    artistName: str
    albumName: str