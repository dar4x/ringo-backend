from typing import Optional
from pydantic import BaseModel

class SongDetailsDTO(BaseModel):
    id: int
    trackName: str
    artistName: str
    plainLyrics: str
    translation: Optional[str] = None
    translationStatus: Optional[str] = None


    class Config: 
        from_attributes = True
    


