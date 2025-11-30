from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, func
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
    translation = Column(Text, nullable=True)
    status = Column(String(20), default='unavailable')

    song = relationship("Song", back_populates="translations")

Song.translations = relationship("SongTranslation", cascade="all, delete-orphan")


class LineDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    original: str
    translation: Optional[str] = None

class SongDetailsDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    trackName: str
    artistName: str
    plainLyrics: str  
    lines: List[LineDTO]  
    translationStatus: str = "unavailable"


class DictionaryWord(Base):
    __tablename__ = "dictionary_words"

    id = Column(Integer, primary_key=True, index=True)
    language = Column(String(10), nullable=False)
    lemma = Column(String, nullable=False)
    normalized = Column(String, nullable=False, index=True)
    translation = Column(Text, nullable=True)
    reading = Column(String, nullable=True)
    pos = Column(String(20), nullable=True)
    hash = Column(String(64), unique=True, index=True)


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    song_id = Column(Integer, ForeignKey("songs.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    progress = Column(Float, default=0.0)


class LessonWord(Base):
    __tablename__ = "lesson_words"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    song_id = Column(Integer, ForeignKey("songs.id"), nullable=False)
    dictionary_word_id = Column(Integer, ForeignKey("dictionary_words.id"), nullable=False)

    status = Column(String(20), default="learn")  # "learn" | "known" | "ignored"
    repetitions = Column(Integer, default=0)
    ease_factor = Column(Float, default=2.5)
    interval = Column(Integer, default=0)
    next_review_at = Column(DateTime(timezone=True), nullable=True)
