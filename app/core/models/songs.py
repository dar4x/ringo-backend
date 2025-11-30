from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database.database import Base

class Song(Base):
    __tablename__ = "songs"
    
    id = Column(Integer, primary_key=True, index=True)
    track_name = Column(String, nullable=False)
    artist_name = Column(String, nullable=False)
    lyrics = Column(Text, nullable=False)
    language = Column(String(10), default="de")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    translations = relationship("SongTranslation", back_populates="song", cascade="all, delete-orphan")

class SongTranslation(Base):
    __tablename__ = "song_translations"
    
    id = Column(Integer, primary_key=True, index=True)
    song_id = Column(Integer, ForeignKey("songs.id"), nullable=False)
    source_language = Column(String(10), default="de")
    target_language = Column(String(10), default="ru")
    translation = Column(Text, nullable=True)
    status = Column(String(20), default="unavailable")
    
    song = relationship("Song", back_populates="translations")