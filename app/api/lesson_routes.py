from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from datetime import datetime
import random

from app.core.database.database import get_db
from app.core.models.songs import Song, Lesson, LessonWord, DictionaryWord
from app.services.normalize_word_service import extract_tokens_ja, lemmatize_token_ja, normalize_key
from app.services.words_service import get_or_create_dictionary_word_ja
from app.services.ja_reading_service import get_reading_from_perplexity
from app.services.srs_service import update_sm2


router = APIRouter(prefix="/lessons", tags=["Lessons"])


@router.get("/{song_id}/word")
async def get_lesson_word(
    song_id: int,
    mode: str = "random",
    translation: bool = True,
    reading: bool = True,
    db: Session = Depends(get_db),
):
    song = db.query(Song).filter(Song.id == song_id).first()
    if not song:
        raise HTTPException(404, "Song not found")

    if song.language != "ja":
        raise HTTPException(400, "This endpoint is for Japanese songs only")

    # 1. Lesson для этой песни
    lesson = db.query(Lesson).filter_by(song_id=song_id).first()
    if not lesson:
        lesson = Lesson(song_id=song_id, progress=0.0)
        db.add(lesson)
        db.commit()
        db.refresh(lesson)

    # 2. Токены
    tokens = extract_tokens_ja(song.lyrics)
    if not tokens:
        raise HTTPException(400, "No tokens found in lyrics")

    # 3. Уникальные леммы
    unique_norms: dict[str, str] = {}
    for t in tokens:
        lemma, _ = lemmatize_token_ja(t)
        norm = lemma.strip()
        if norm and norm not in unique_norms:
            unique_norms[norm] = t

    # 4. Кандидаты, которых ещё нет в этом уроке
    candidates: list[tuple[str, str]] = []

    for norm, token in unique_norms.items():
        h = normalize_key("ja", norm)
        dict_word = db.query(DictionaryWord).filter_by(hash=h).first()
        if dict_word:
            lw = (
                db.query(LessonWord)
                .filter_by(
                    lesson_id=lesson.id,
                    dictionary_word_id=dict_word.id,
                )
                .first()
            )
            if lw:
                continue  # это слово уже есть в уроке
        candidates.append((norm, token))

    if not candidates:
        return {"message": "No new words to learn for this lesson"}

    norm, token = random.choice(candidates)

    # 5. Словарное слово (с переводом, если нужно)
    dict_word = await get_or_create_dictionary_word_ja(
        token=token,
        db=db,
        need_translation=translation,
    )

    # 6. Чтение, если нужно
    if reading and not dict_word.reading:
        reading_value = await get_reading_from_perplexity(dict_word.lemma)
        if reading_value:
            dict_word.reading = reading_value
            db.commit()
            db.refresh(dict_word)

    # 7. LessonWord
    lw = LessonWord(
        lesson_id=lesson.id,
        song_id=song_id,
        dictionary_word_id=dict_word.id,
        status="learn",
    )
    db.add(lw)
    db.commit()
    db.refresh(lw)

    display = dict_word.lemma
    if dict_word.reading:
        display = f"{dict_word.lemma} ({dict_word.reading})"

    return {
        "songId": song_id,
        "lessonId": lesson.id,
        "lessonWordId": lw.id,
        "word": dict_word.lemma,
        "reading": dict_word.reading,
        "display": display,
        "translation": dict_word.translation,
        "language": dict_word.language,
        "nextReviewAt": lw.next_review_at.isoformat() if lw.next_review_at else None,
    }


@router.post("/word/{lesson_word_id}/review")
async def review_lesson_word(
    lesson_word_id: int,
    grade: int = Body(..., ge=0, le=5),
    db: Session = Depends(get_db),
):
    lw = db.query(LessonWord).filter_by(id=lesson_word_id).first()
    if not lw:
        raise HTTPException(404, "Lesson word not found")

    now = datetime.utcnow()
    update_sm2(lw, grade, now)

    if grade >= 4 and lw.repetitions >= 3:
        lw.status = "known"

    db.commit()

    return {
        "lessonWordId": lw.id,
        "status": lw.status,
        "nextReviewAt": lw.next_review_at.isoformat() if lw.next_review_at else None,
    }
