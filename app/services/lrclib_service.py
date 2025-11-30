from app.core.config import LRCLIB_API
from app.core.http_client import async_client
from app.core.models.songs import LineDTO, Song, SongDetailsDTO, SongTranslation
from sqlalchemy.orm import Session
from typing import Optional
from app.models.dto_song_search import SongSearchDTO
from app.services.encoding_utils import fix_mojibake
from app.services.perplexity_service import translate_song_lyrics


async def search_song(
    q: str = None,
    track_name: str = None,
    artist_name: str = None,
    album_name: str = None,
) -> list[SongSearchDTO]:
    params = {
        "q": q,
        "track_name": track_name,
        "artist_name": artist_name,
        "album_name": album_name,
    }

    resp = await async_client.get(LRCLIB_API + "search", params=params)
    resp.raise_for_status()
    data = resp.json()

    if not isinstance(data, list):
        return []

    print(f"LRCLIB search returned {len(data)} items")

    results: list[SongSearchDTO] = []

    for idx, raw in enumerate(data):
        raw_track = raw.get("trackName") or ""
        raw_artist = raw.get("artistName") or ""
        raw_album  = raw.get("albumName") or ""

        # если вообще пусто по всем трём — пропускаем
        if not (raw_track or raw_artist or raw_album):
            print(f"⚠️ Skipping item {idx}: empty track/artist/album")
            continue

        track_fixed  = fix_mojibake(raw_track)
        artist_fixed = fix_mojibake(raw_artist)
        album_fixed  = fix_mojibake(raw_album)

        dto = SongSearchDTO(
            id=raw.get("id"),
            trackName=track_fixed,
            artistName=artist_fixed,
            albumName=album_fixed,
        )
        results.append(dto)

    print(f"Returning {len(results)} valid items")
    return results




async def song_id(id: int, db: Session) -> Optional[SongDetailsDTO]:
    print(f"🔍 Поиск песни {id}")
    song = db.query(Song).filter(Song.id == id).first()

    # 1. Если песни нет в БД — тянем из LRCLIB и сохраняем, БЕЗ автоперевода
    if not song:
        try:
            resp = await async_client.get(f"{LRCLIB_API}get/{id}")
            resp.raise_for_status()
            data = resp.json()
            if not isinstance(data, dict):
                return None
            
            track_name = fix_mojibake(data["trackName"])
            artist_name = fix_mojibake(data["artistName"])
            lyrics = fix_mojibake(data["plainLyrics"])

            song = Song(
                id=data["id"],
                track_name=track_name,
                artist_name=artist_name,
                lyrics=lyrics,
                language="ja",  # или de/ja — по ситуации
            )
            db.add(song)
            db.commit()
            db.refresh(song)
        except Exception as e:
            print(f"LRCLIB error: {e}")
            return None

    print(f"✅ Song найдена: {song.track_name}")

    # 2. Пробуем найти готовый перевод
    translation = db.query(SongTranslation).filter(
        SongTranslation.song_id == id,
        SongTranslation.target_language == "ru",
    ).first()

    # 3. Если перевода нет — ОДИН раз делаем автоперевод
    if not translation:
        print("🚀 Автоперевод в song_id()")
        translation_text = await translate_song_lyrics(song.lyrics)
        status = "ready" if translation_text else "unavailable"

        translation = SongTranslation(
            song_id=id,
            source_language=song.language,
            target_language="ru",
            translation=translation_text,
            status=status,
        )
        db.add(translation)
        db.commit()
        db.refresh(translation)

    # 4. Построчный разбор
    original_lines = [line.strip() for line in song.lyrics.splitlines() if line.strip()]
    translated_lines: list[str] = []

    if translation.translation and translation.status == "ready":
        translated_lines = [
            line.strip()
            for line in translation.translation.splitlines()
            if line.strip()
        ]

    lines: list[LineDTO] = []
    for i, orig in enumerate(original_lines):
        trans = translated_lines[i] if i < len(translated_lines) else None
        lines.append(
            LineDTO(
                original=f"[translate:{orig}]",
                translation=trans,
            )
        )

    return SongDetailsDTO(
        id=song.id,
        trackName=fix_mojibake(song.track_name),
        artistName=fix_mojibake(song.artist_name),
        plainLyrics=fix_mojibake(song.lyrics),
        lines=lines,
        translationStatus=translation.status,
    )
