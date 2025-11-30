from typing import Optional
from app.core.config import PERPLEXITY_API_KEY
from app.core.http_client import async_client


async def get_reading_from_perplexity(lemma: str) -> Optional[str]:
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
                        "Ты преподаватель. Дай ТОЛЬКО чтение этого слова "
                        "на ромадзи (латиницей), без перевода и лишних слов."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Напиши ромадзи для слова: {lemma}",
                },
            ],
        },
        timeout=15.0,
    )

    if resp.status_code != 200:
        return None

    data = resp.json()
    content = data["choices"][0]["message"]["content"].strip()
    return content.splitlines()[0].strip() or None
