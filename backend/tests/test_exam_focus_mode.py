import json
import pytest
from datetime import timedelta
from types import SimpleNamespace

from django.core.cache import cache
from django.test import RequestFactory
from django.utils import timezone

from apps.exams.models import Exam
from config.exam_focus_middleware import ExamFocusModeMiddleware


@pytest.mark.django_db
def test_focus_mode_blocks_non_exam_features_but_keeps_exam_and_staff_access():
    now = timezone.now()
    exam = Exam.objects.create(
        title="آزمون سراسری",
        kind=Exam.Kind.WEEKLY,
        duration_minutes=30,
        starts_at=now - timedelta(minutes=2),
        ends_at=now + timedelta(minutes=28),
        status=Exam.Status.PUBLISHED,
    )
    cache.clear()
    factory = RequestFactory()
    middleware = ExamFocusModeMiddleware(lambda request: SimpleNamespace(status_code=200))

    regular_user = SimpleNamespace(is_authenticated=True, is_staff=False)
    question_request = factory.get("/api/v1/questions/")
    question_request.user = regular_user
    blocked = middleware(question_request)
    assert blocked.status_code == 423
    assert json.loads(blocked.content)["code"] == "EXAM_FOCUS_MODE"

    exam_request = factory.get(f"/api/v1/exams/{exam.pk}/start/")
    exam_request.user = regular_user
    assert middleware(exam_request).status_code == 200

    admin_request = factory.get("/api/v1/questions/")
    admin_request.user = SimpleNamespace(is_authenticated=True, is_staff=True)
    assert middleware(admin_request).status_code == 200


@pytest.mark.django_db
def test_focus_mode_automatically_ends_at_official_deadline(monkeypatch):
    now = timezone.now()
    deadline = now + timedelta(minutes=5)
    Exam.objects.create(
        title="آزمون زمان‌بندی‌شده",
        kind=Exam.Kind.WEEKLY,
        duration_minutes=10,
        starts_at=now - timedelta(minutes=5),
        ends_at=deadline,
        status=Exam.Status.PUBLISHED,
    )
    cache.clear()
    factory = RequestFactory()
    middleware = ExamFocusModeMiddleware(lambda request: SimpleNamespace(status_code=200))
    request = factory.get("/api/v1/payments/plans/")
    request.user = SimpleNamespace(is_authenticated=True, is_staff=False)

    before_deadline = middleware(request)
    assert before_deadline.status_code == 423

    monkeypatch.setattr("apps.exams.focus.timezone.now", lambda: deadline)
    cache.clear()
    at_deadline = middleware(request)
    assert at_deadline.status_code == 200
