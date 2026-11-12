from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from apps.exams.models import Exam, ExamQuestion
from apps.exams.services import finalize_attempt, save_answer, start_attempt
from apps.questions.models import Question, QuestionOption


class ExamEngineTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(phone_number="09121111111")
        author = get_user_model().objects.create_user(phone_number="09122222222")
        reviewer = get_user_model().objects.create_user(phone_number="09123333333")
        question = Question.objects.create(
            subject=Question.Subject.DIRECT_TAX, prompt="سؤال تستی؟",
            author=author, reviewer=reviewer, status=Question.Status.DRAFT,
        )
        self.options = []
        for pos in range(1, 5):
            self.options.append(QuestionOption.objects.create(
                question=question, position=pos, text=f"گزینه {pos}", is_correct=(pos == 1)
            ))
        question.status = Question.Status.PUBLISHED
        question.save()
        self.exam = Exam.objects.create(
            title="آزمون آزمایشی", kind=Exam.Kind.DAILY,
            duration_minutes=20, status=Exam.Status.DRAFT,
        )
        ExamQuestion.objects.create(exam=self.exam, question=question, position=1)
        self.exam.status = Exam.Status.PUBLISHED
        self.exam.save()

    def test_attempt_snapshots_questions_and_hides_correctness(self):
        attempt = start_attempt(self.exam.pk, self.user)
        snapshot = attempt.questions.get()
        self.assertEqual(snapshot.options.count(), 4)
        self.assertFalse(hasattr(snapshot.options.first(), "correct_answer"))
        self.assertEqual(attempt.status, "in_progress")

    def test_answer_and_finalize_are_server_graded(self):
        attempt = start_attempt(self.exam.pk, self.user)
        question = attempt.questions.get()
        correct_option = question.options.get(is_correct=True)
        save_answer(attempt.pk, question.pk, correct_option.pk, self.user)
        result = finalize_attempt(attempt.pk, self.user)
        self.assertEqual(result.correct_count, 1)
        self.assertEqual(result.score, 10)
        self.assertEqual(finalize_attempt(attempt.pk, self.user).score, 10)
