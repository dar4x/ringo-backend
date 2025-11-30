from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database.database import get_db
from app.core.models.songs import DictionaryWord
from app.services.ja_reading_service import get_reading_from_perplexity
from app.services.normalize_word_service import normalize_key

router = APIRouter(prefix="/words", tags=["Words"])


@router.get("/ja/reading")
async def get_ja_reading(
    text: str,
    db: Session = Depends(get_db),
):
    """
    GET /words/ja/reading?text=今
    """
    lemma = text.strip()
    if not lemma:
        raise HTTPException(400, "Text is required")

    norm = lemma  # на MVP нормализация = само слово
    h = normalize_key("ja", norm)

    word = db.query(DictionaryWord).filter_by(hash=h).first()
    if word and word.reading:
        display = f"{word.lemma} ({word.reading})"
        return {
            "wordId": word.id,
            "word": word.lemma,
            "reading": word.reading,
            "display": display,
        }

    # либо слова вообще нет, либо нет reading → создаём/обновляем
    if not word:
        word = DictionaryWord(
            language="ja",
            lemma=lemma,
            normalized=norm,
            translation=None,
            reading=None,
            hash=h,
        )
        db.add(word)
        db.commit()
        db.refresh(word)

    reading = await get_reading_from_perplexity(lemma)
    if reading:
        word.reading = reading
        db.commit()
        db.refresh(word)

    display = f"{word.lemma} ({word.reading})" if word.reading else word.lemma

    return {
        "wordId": word.id,
        "word": word.lemma,
        "reading": word.reading,
        "display": display,
    }
