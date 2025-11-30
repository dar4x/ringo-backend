from app.core.config import PERPLEXITY_API_KEY
from typing import Optional
from app.core.http_client import async_client

async def translate_song_lyrics(lyrics:str, target_lang: str = 'ru') -> Optional[str]:
    if not PERPLEXITY_API_KEY:
        return None
    
    response = await async_client.post(
        "https://api.perplexity.ai/chat/completions",
        headers={
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "sonar-small-online",
            "messages": [
                {
                    "role": "system",
                    "content": "Ты переводчик песен. Сохраняй структуру строк, не добавляй комментарии."
                },
                {
                    "role": "user",
                    "content": f"Переведи текст песни на русский:\n\n{lyrics}"
                }
            ]
        },
        timeout=10.0

    )

    if response.status_code == 200:
        content = response.json()["choices"][0]["message"]["content"]
        return content.strip()
    return None