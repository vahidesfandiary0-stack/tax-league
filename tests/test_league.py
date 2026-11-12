from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from apps.exams.models import Exam, ExamAttempt
from apps.league.models import LeagueScoreEntry, LeagueSeason
from apps.league.services import record_attempt_score


class LeagueLedgerTests(TestCase):
    def setUp(self):
        now = timezone.now()
        self.season = LeagueSeason.objects.create(
            title="آزمایشی",
            starts_at=now - timedelta(days=1),
            ends_at=now + timedelta(days=1),
            status=LeagueSeason.Status.ACTIVE,
        )
        self.user = get_user_model().objects.create_user(
            phone_number="09120000001",
            display_name="شرکت‌کننده",
        )
        self.exam = Exam.objects.create(
            title="آزمون رسمی",
            kind=Exam.Kind.WEEKLY,
            duration_minutes=30,
            counts_for_league=True,
            status=Exam.Status.PUBLISHED,
        )
        self.attempt = ExamAttempt.objects.create(
            exam=self.exam,
            user=self.user,
            status=ExamAttempt.Status.SUBMITTED,
            started_at=now - timedelta(minutes=10),
            deadline_at=now + timedelta(minutes=20),
            submitted_at=now,
            score=37,
            correct_count=4,
            wrong_count=1,
            blank_count=0,
        )

    def test_recording_same_attempt_is_idempotent(self):
        first = record_attempt_score(self.attempt.pk)
        second = record_attempt_score(self.attempt.pk)
        self.assertEqual(first.pk, second.pk)
        self.assertEqual(LeagueScoreEntry.objects.filter(attempt=self.attempt).count(), 1)

    def test_ledger_entry_cannot_be_edited(self):
        entry = record_attempt_score(self.attempt.pk)
        entry.score = 999
        with self.assertRaises(ValidationError):
            entry.save()
