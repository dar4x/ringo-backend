from pydantic import BaseModel

class SongDetailsDTO(BaseModel):
    id: int
    trackName: str
    artistName: str
    plainLyrics: str


