from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from apps.accounts.models import User
from apps.exams.models import Exam, ExamAttempt, ExamQuestion
from apps.league.models import LeagueScoreEntry, LeagueSeason
from apps.league.services import activate_season, record_attempt_score
from apps.questions.models import Question, QuestionOption
from apps.exams.services import finalize_attempt, publish_exam, save_answer, start_attempt


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

    def test_night_exam_can_publish_and_score_a_pending_review_question(self):
        now = timezone.now()
        question = Question.objects.create(
            subject=Question.Subject.DIRECT_TAX,
            prompt="سؤال در انتظار بررسی",
            explanation="توضیح پاسخ",
            status=Question.Status.PENDING,
            author=self.user,
        )
        for position in range(1, 5):
            QuestionOption.objects.create(
                question=question,
                position=position,
                text=f"گزینه {position}",
                is_correct=(position == 2),
            )

        season = LeagueSeason.objects.create(
            title="فصل آزمایشی آزمون بررسی‌نشده",
            starts_at=now - timedelta(minutes=10),
            ends_at=now + timedelta(hours=1),
        )
        activate_season(season.pk, self.user)

        exam = Exam.objects.create(
            title="آزمون شبانه با سؤال بررسی‌نشده",
            kind=Exam.Kind.NIGHT,
            duration_minutes=30,
            starts_at=now - timedelta(minutes=5),
            ends_at=now + timedelta(minutes=25),
            counts_for_league=True,
            requires_purchase=False,
        )
        ExamQuestion.objects.create(exam=exam, question=question, position=1)
        published = publish_exam(exam.pk)
        self.assertEqual(published.status, Exam.Status.PUBLISHED)

        attempt = start_attempt(exam.pk, self.user)
        attempt_question = attempt.questions.first()
        correct_option = attempt_question.options.get(is_correct=True)
        save_answer(attempt.pk, attempt_question.pk, correct_option.pk, self.user)
        result = finalize_attempt(attempt.pk, self.user)
        self.assertEqual(result.status, ExamAttempt.Status.SUBMITTED)
        self.assertEqual(result.correct_count, 1)
        self.assertEqual(result.score, 10)
        self.assertTrue(LeagueScoreEntry.objects.filter(attempt=result, season=season).exists())

