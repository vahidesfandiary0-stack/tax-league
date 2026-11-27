from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from apps.exams.models import Exam, ExamAttempt
from apps.league.models import LeagueSeason, LeagueScoreEntry


User = get_user_model()


class MyTopRecordsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            phone_number="09120000111",
            display_name="آزمایش رکوردها",
        )
        self.client.force_authenticate(self.user)
        now = timezone.now()
        self.season = LeagueSeason.objects.create(
            title="فصل رکوردها",
            starts_at=now - timedelta(days=10),
            ends_at=now + timedelta(days=10),
            status=LeagueSeason.Status.ACTIVE,
        )

    def add_result(self, title, score, correct, wrong=0, elapsed=600):
        now = timezone.now()
        exam = Exam.objects.create(
            title=title,
            kind=Exam.Kind.NIGHT,
            duration_minutes=30,
            max_attempts=1,
            starts_at=now - timedelta(days=2),
            ends_at=now - timedelta(hours=1),
            status=Exam.Status.PUBLISHED,
            counts_for_league=True,
            requires_purchase=False,
            price_irr=0,
        )
        attempt = ExamAttempt.objects.create(
            exam=exam,
            user=self.user,
            status=ExamAttempt.Status.SUBMITTED,
            started_at=now - timedelta(minutes=30),
            deadline_at=now + timedelta(minutes=1),
            submitted_at=now,
            score=score,
            correct_count=correct,
            wrong_count=wrong,
            blank_count=0,
        )
        LeagueScoreEntry.objects.create(
            season=self.season,
            attempt=attempt,
            user=self.user,
            score=score,
            correct_count=correct,
            wrong_count=wrong,
            elapsed_seconds=elapsed,
        )
        return attempt

    def get_records(self):
        return self.client.get("/api/v1/league/me/top-records/")

    def test_one_valid_result_is_returned_as_one_record(self):
        attempt = self.add_result("آزمون اول", 72, 8, 2)

        response = self.get_records()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["attempt_id"], str(attempt.pk)
        )

    def test_two_valid_results_are_both_returned(self):
        first = self.add_result("آزمون اول", 72, 8, 2)
        second = self.add_result("آزمون دوم", 81, 9, 1)

        response = self.get_records()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertEqual(
            [row["attempt_id"] for row in response.data["results"]],
            [str(second.pk), str(first.pk)],
        )

    def test_more_than_five_results_returns_only_five_best(self):
        attempts = [
            self.add_result(f"آزمون {score}", score, score // 10)
            for score in [30, 95, 55, 80, 65, 100, 45]
        ]

        response = self.get_records()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 5)
        self.assertEqual(
            [row["score"] for row in response.data["results"]],
            [100, 95, 80, 65, 55],
        )
        returned_ids = [row["attempt_id"] for row in response.data["results"]]
        self.assertNotIn(str(attempts[0].pk), returned_ids)
        self.assertNotIn(str(attempts[6].pk), returned_ids)

    def test_endpoint_requires_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.get_records()

        self.assertEqual(response.status_code, 401)
