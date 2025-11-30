from sqlalchemy.orm import Session
from typing import Optional

from app.core.models.songs import DictionaryWord
from app.services.normalize_word_service import normalize_key, lemmatize_token_ja
from app.services.translate_word_service import translate_word_once_ja


async def get_or_create_dictionary_word_ja(
    token: str,
    db: Session,
    need_translation: bool = True,
) -> DictionaryWord:
    lemma, reading = lemmatize_token_ja(token)
    normalized = lemma.strip()
    h = normalize_key("ja", normalized)

    word = db.query(DictionaryWord).filter_by(hash=h).first()
    if word:
        return word

    translation: Optional[str] = None
    if need_translation:
        translation = await translate_word_once_ja(lemma)

    word = DictionaryWord(
        language="ja",
        lemma=lemma,
        normalized=normalized,
        translation=translation,
        reading=reading or None,
        hash=h,
    )
    db.add(word)
    db.commit()
    db.refresh(word)
    return word
