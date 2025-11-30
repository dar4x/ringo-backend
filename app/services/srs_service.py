from datetime import datetime, timedelta
from app.core.models.songs import LessonWord


def update_sm2(lw: LessonWord, grade: int, now: datetime) -> None:
    if grade < 3:
        lw.repetitions = 0
        lw.interval = 1
    else:
        if lw.repetitions == 0:
            lw.interval = 1
        elif lw.repetitions == 1:
            lw.interval = 6
        else:
            lw.interval = int(lw.interval * lw.ease_factor)
        lw.repetitions += 1

    lw.ease_factor = max(
        1.3,
        lw.ease_factor + (0.1 - (5 - grade) * (0.08 + (5 - grade) * 0.02)),
    )
    lw.next_review_at = now + timedelta(days=lw.interval)
