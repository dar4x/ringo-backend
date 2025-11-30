from typing import Optional
from app.core.config import PERPLEXITY_API_KEY
from app.core.http_client import async_client


async def translate_word_once_ja(lemma: str) -> Optional[str]:
    if not PERPLEXITY_API_KEY:
        return None

    resp = await async_client.post(
        "https://api.perplexity.ai/chat/completions",
        headers={
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "sonar",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Ты преподаватель. Дай КРАТКИЙ перевод одного "
                        "Переведи слова на русский (1–3 слова), без примеров."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Переведи слово на русский: {lemma}",
                },
            ],
        },
        timeout=15.0,
    )

    if resp.status_code != 200:
        return None

    data = resp.json()
    content = data["choices"][0]["message"]["content"].strip()
    return content.splitlines()[0].strip()
