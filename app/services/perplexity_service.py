import httpx
from typing import Optional
from app.core.config import PERPLEXITY_API_KEY
from app.core.http_client import async_client

COPYRIGHT_MARKERS = [
    "не могу предоставить полный перевод текста этой песни",
    "это было бы воспроизведением защищённого авторским правом материала",
    "i cannot provide a full translation of this song",
]

def is_copyright_refusal(text: str) -> bool:
    lower = text.lower()
    return any(marker in lower for marker in COPYRIGHT_MARKERS)


async def translate_song_lyrics(lyrics: str, target_lang: str = "ru") -> Optional[str]:
    print(f"🔑 PERPLEXITY_API_KEY: {'OK' if PERPLEXITY_API_KEY else 'MISSING'}")
    if not PERPLEXITY_API_KEY:
        print("❌ NO API KEY")
        return None
    
    try:
        print("🚀 Calling Perplexity...")
        response = await async_client.post(
            "https://api.perplexity.ai/chat/completions",
            headers={
                "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "sonar",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Ты переводчик песен. ПЕРЕВОДИ ТОЧНО ПО СТРОКАМ. "
                            "НЕ добавляй вступления/комментарии. Только перевод "
                            "с теми же переносами строк."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"Переведи СТРОКАМИ на русский:\n\n{lyrics}",
                    },
                ],
            },
            timeout=30.0,
        )
        
        print(f"📡 Status: {response.status_code}")
        print(f"📄 Response preview: {response.text[:200]}...")
        
        if response.status_code != 200:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return None
        
        data = response.json()
        content = data["choices"][0]["message"]["content"].strip()
        print(f"✅ Translation: {content[:100]}...")
        
        if is_copyright_refusal(content):
            print("⚠️ Detected copyright refusal from Perplexity")
            return None
        
        return content
    
    except Exception as e:
        print(f"💥 Exception: {e}")
        return None
