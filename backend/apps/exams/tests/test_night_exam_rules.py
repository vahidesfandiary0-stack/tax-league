from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from apps.accounts.models import User
from apps.exams.models import Exam, ExamAttempt
from apps.league.services import record_attempt_score


class NightExamRulesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("+989120000001")

    def test_non_night_exam_cannot_count_for_league(self):
        exam = Exam(
            title="آزمون روزانه آزمایشی",
            kind=Exam.Kind.DAILY,
            counts_for_league=True,
        )
        with self.assertRaises(ValidationError):
            exam.clean()

    def test_night_exam_must_have_a_valid_schedule(self):
        exam = Exam(title="آزمون شبانه بدون زمان", kind=Exam.Kind.NIGHT, counts_for_league=True)
        with self.assertRaises(ValidationError):
            exam.clean()

    def test_night_exam_must_count_for_league(self):
        exam = Exam(
            title="آزمون شبانه غیررسمی",
            kind=Exam.Kind.NIGHT,
            starts_at=timezone.now(),
            ends_at=timezone.now() + timedelta(minutes=30),
        )
        with self.assertRaises(ValidationError):
            exam.clean()

    def test_night_exam_must_be_free(self):
        exam = Exam(
            title="آزمون شبانه آزمایشی",
            kind=Exam.Kind.NIGHT,
            counts_for_league=True,
            starts_at=timezone.now(),
            ends_at=timezone.now() + timedelta(minutes=30),
            requires_purchase=True,
            price_irr=1000,
        )
        with self.assertRaises(ValidationError):
            exam.clean()

    def test_only_night_exam_can_write_league_score(self):
        now = timezone.now()
        exam = Exam.objects.create(
            title="آزمون روزانه بدون اثر بر لیگ",
            kind=Exam.Kind.DAILY,
            counts_for_league=False,
        )
        attempt = ExamAttempt.objects.create(
            exam=exam,
            user=self.user,
            status=ExamAttempt.Status.SUBMITTED,
            started_at=now - timedelta(minutes=5),
            deadline_at=now + timedelta(minutes=25),
            submitted_at=now,
            score=10,
            correct_count=1,
        )
        self.assertIsNone(record_attempt_score(attempt.pk))
