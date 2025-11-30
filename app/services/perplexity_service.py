import httpx
from app.core.config import PERPLEXITY_API_KEY
from app.core.http_client import async_client
from typing import Optional

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
        "content": "Ты профессиональный переводчик песен. Автоматически определи язык текста и переведи на русский. Сохрани количество строк и структуру. Не добавляй комментарии."
    },
    {
        "role": "user", 
        "content": f"Переведи текст песни, сохранив все переносы строк:\n\n{lyrics}"
    }
]

            },
            timeout=30.0
        )
        
        print(f"📡 Status: {response.status_code}")
        print(f"📄 Response preview: {response.text[:200]}...")
        
        if response.status_code == 200:
            data = response.json()
            content = data["choices"][0]["message"]["content"].strip()
            print(f"✅ Translation: {content[:100]}...")
            return content
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"💥 Exception: {e}")
        return None
import httpx
from app.core.config import PERPLEXITY_API_KEY
from app.core.http_client import async_client
from typing import Optional

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
        "content": "Ты профессиональный переводчик песен. Автоматически определи язык текста и переведи на русский. Сохрани количество строк и структуру. Не добавляй комментарии."
    },
    {
        "role": "user", 
        "content": f"Переведи текст песни, сохранив все переносы строк:\n\n{lyrics}"
    }
]

            },
            timeout=30.0
        )
        
        print(f"📡 Status: {response.status_code}")
        print(f"📄 Response preview: {response.text[:200]}...")
        
        if response.status_code == 200:
            data = response.json()
            content = data["choices"][0]["message"]["content"].strip()
            print(f"✅ Translation: {content[:100]}...")
            return content
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"💥 Exception: {e}")
        return None
