from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.accounts.models import User
from apps.exams.models import Exam, ExamAttempt
from apps.league.models import LeagueSeason, LeagueScoreEntry
from apps.league.services import record_attempt_score


class LeagueExamEligibilityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("09120000021")
        now = timezone.now()
        self.season = LeagueSeason.objects.create(
            title="فصل آزمون شبانه",
            starts_at=now - timedelta(days=1),
            ends_at=now + timedelta(days=1),
            status=LeagueSeason.Status.ACTIVE,
        )

    def _attempt(self, kind, counts_for_league=True):
        now = timezone.now()
        exam = Exam.objects.create(
            title="آزمون آزمایشی",
            kind=kind,
            status=Exam.Status.PUBLISHED,
            counts_for_league=counts_for_league,
        )
        return ExamAttempt.objects.create(
            exam=exam,
            user=self.user,
            status=ExamAttempt.Status.SUBMITTED,
            started_at=now - timedelta(minutes=10),
            deadline_at=now + timedelta(minutes=20),
            submitted_at=now,
            score=80,
            correct_count=8,
            wrong_count=0,
            blank_count=0,
        )

    def test_only_nightly_exam_with_league_flag_creates_score_entry(self):
        daily = self._attempt(Exam.Kind.DAILY, counts_for_league=True)
        weekly = self._attempt(Exam.Kind.WEEKLY, counts_for_league=True)
        nightly_disabled = self._attempt(Exam.Kind.NIGHTLY, counts_for_league=False)
        nightly = self._attempt(Exam.Kind.NIGHTLY, counts_for_league=True)

        self.assertIsNone(record_attempt_score(daily.pk))
        self.assertIsNone(record_attempt_score(weekly.pk))
        self.assertIsNone(record_attempt_score(nightly_disabled.pk))
        entry = record_attempt_score(nightly.pk)

        self.assertIsInstance(entry, LeagueScoreEntry)
        self.assertEqual(entry.season_id, self.season.pk)
        self.assertEqual(entry.user_id, self.user.pk)
