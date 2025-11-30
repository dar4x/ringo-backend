from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship
from app.core.database.database import Base


class Song(Base): 
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True, index=True)
    track_name = Column(String, nullable=False)
    artist_name = Column(String, nullable=False)
    lyrics = Column(Text, nullable=False)
    language = Column(String(10), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SongTranslation(Base): 
    __tablename__ = "song_translations"

    id = Column(Integer, primary_key= True, index=True)
    song_id = Column(Integer, ForeignKey("songs.id"), nullable=False)
    source_language = Column(String(10), nullable=False)
    target_language = Column(String(10), nullable=False)
    translation = Column(Text, nullable=False)
    status = Column(String(20), default='unavailable')

    song = relationship("Song", back_populates="translations")

Song.translations = relationship("SongTranslation", cascade="all, delete-orphan")
