from datetime import timedelta

from django.core.cache import cache
from django.utils import timezone

from .models import Exam


CACHE_KEY = "tax_league:exam_focus_mode:v1"
CACHE_TTL_SECONDS = 2


def get_exam_focus_state(now=None):
    """Return the shared focus-mode window derived from published scheduled exams."""
    if now is None:
        cached = cache.get(CACHE_KEY)
        if cached is not None:
            return cached
        now = timezone.now()
        use_cache = True
    else:
        use_cache = False

    active_deadlines = []
    exams = Exam.objects.filter(
        status=Exam.Status.PUBLISHED,
        starts_at__isnull=False,
        starts_at__lte=now,
    ).only("id", "title", "starts_at", "ends_at", "duration_minutes")

    for exam in exams.iterator():
        deadline = exam.starts_at + timedelta(minutes=exam.duration_minutes)
        if exam.ends_at:
            deadline = min(deadline, exam.ends_at)
        if now < deadline:
            active_deadlines.append((deadline, exam.title, str(exam.pk)))

    if active_deadlines:
        deadline, title, exam_id = max(active_deadlines, key=lambda item: item[0])
        state = {
            "active": True,
            "ends_at": deadline.isoformat(),
            "exam_title": title,
            "exam_id": exam_id,
        }
    else:
        state = {"active": False, "ends_at": None, "exam_title": None, "exam_id": None}

    if use_cache:
        cache.set(CACHE_KEY, state, CACHE_TTL_SECONDS)
    return state
