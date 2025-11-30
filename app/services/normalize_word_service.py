import hashlib
from typing import Tuple, List


def normalize_key(language: str, lemma: str) -> str:
    base = f"{language.lower()}|{lemma.strip()}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


def extract_tokens_ja(text: str) -> List[str]:
    # MVP: очень грубо — разбить по пробелам и переносам,
    # плюс отдельно канжи/каны без пунктуации.
    lines = text.splitlines()
    tokens: List[str] = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # японский обычно без пробелов: просто добавляем строки целиком
        tokens.append(line)
    return tokens


def lemmatize_token_ja(token: str) -> Tuple[str, str]:

    lemma = token
    reading = ""
    return lemma, reading
