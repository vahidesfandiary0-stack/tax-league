from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.exams.models import Exam, ExamAttempt


@pytest.mark.django_db
def test_results_endpoint_returns_only_authenticated_users_own_finished_attempts():
    User = get_user_model()
    owner = User.objects.create_user(phone_number="09121110001")
    other = User.objects.create_user(phone_number="09121110002")
    exam = Exam.objects.create(title="آزمون تاریخچه", kind=Exam.Kind.DAILY)
    own = ExamAttempt.objects.create(
        exam=exam, user=owner, status=ExamAttempt.Status.SUBMITTED,
        started_at=timezone.now(), deadline_at=timezone.now() + timedelta(minutes=30),
        submitted_at=timezone.now(), score=17, correct_count=2, wrong_count=1, blank_count=0,
    )
    ExamAttempt.objects.create(
        exam=exam, user=other, status=ExamAttempt.Status.SUBMITTED,
        started_at=timezone.now(), deadline_at=timezone.now() + timedelta(minutes=30),
        submitted_at=timezone.now(), score=99,
    )
    ExamAttempt.objects.create(
        exam=exam, user=owner, status=ExamAttempt.Status.IN_PROGRESS,
        started_at=timezone.now(), deadline_at=timezone.now() + timedelta(minutes=30),
    )

    client = APIClient()
    client.force_authenticate(user=owner)
    response = client.get(reverse("my-exam-results"))

    assert response.status_code == 200
    assert len(response.data) == 1
    assert str(response.data[0]["id"]) == str(own.pk)
    assert response.data[0]["exam_title"] == "آزمون تاریخچه"
    assert response.data[0]["score"] == 17


@pytest.mark.django_db
def test_results_endpoint_requires_authentication():
    response = APIClient().get(reverse("my-exam-results"))
    assert response.status_code in (401, 403)
