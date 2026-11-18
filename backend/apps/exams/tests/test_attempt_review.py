from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.exams.models import (
    AttemptOption, AttemptQuestion, Exam, ExamAttempt,
)
from apps.payments.models import PaymentOrder
from apps.questions.models import Question, QuestionPremiumLesson
from apps.subscriptions.models import SubscriptionPlan, UserSubscription
from apps.questions.services import (
    publish_premium_lesson,
    review_premium_lesson,
    submit_premium_lesson_for_review,
)


class AttemptReviewAccessTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user("09120000001")
        self.other_user = User.objects.create_user("09120000002")
        self.reviewer = User.objects.create_user("09120000003")
        self.question = Question.objects.create(
            subject=Question.Subject.VAT,
            prompt="متن سؤال آزمایشی",
            explanation="پاسخ تشریحی عمومی",
            author=self.user,
        )
        self.exam = Exam.objects.create(
            title="آزمون آزمایشی",
            kind=Exam.Kind.DAILY,
            status=Exam.Status.PUBLISHED,
        )
        self.attempt = self._make_attempt(self.user, ExamAttempt.Status.SUBMITTED)
        self.lesson = QuestionPremiumLesson.objects.create(
            question=self.question,
            traps_and_techniques="تله اصلی",
            trap_detection_signals="نشانه تشخیص",
            distractor_analysis="تحلیل گزینه‌های انحرافی",
            fast_solving_method="روش سریع",
            setter_insight="نکته حرفه‌ای طراح",
            common_mistakes="خطای رایج",
            supplementary_practice="تمرین تکمیلی",
            practice_answer="پاسخ تمرین",
            author=self.user,
        )
        submit_premium_lesson_for_review(self.lesson.pk, self.user)
        review_premium_lesson(self.lesson.pk, self.reviewer, approve=True)
        publish_premium_lesson(self.lesson.pk)
        self.lesson.refresh_from_db()

    def _make_attempt(self, owner, status):
        attempt = ExamAttempt.objects.create(
            exam=self.exam,
            user=owner,
            status=status,
            started_at=timezone.now() - timedelta(minutes=10),
            deadline_at=timezone.now() + timedelta(minutes=20),
            submitted_at=timezone.now() if status != ExamAttempt.Status.IN_PROGRESS else None,
        )
        snapshot = AttemptQuestion.objects.create(
            attempt=attempt,
            source_question_id=self.question.pk,
            position=1,
            prompt=self.question.prompt,
            explanation=self.question.explanation,
            subject=self.question.subject,
        )
        correct = AttemptOption.objects.create(
            attempt_question=snapshot, source_option_id=1,
            position=1, text="گزینه صحیح", is_correct=True,
        )
        AttemptOption.objects.create(
            attempt_question=snapshot, source_option_id=2,
            position=2, text="گزینه نادرست", is_correct=False,
        )
        return attempt

    def _grant_subscription(self, ends_at):
        plan = SubscriptionPlan.objects.create(
            title="آزمایشی", period=SubscriptionPlan.Period.MONTHLY,
            duration_days=30, price_irr=100000,
        )
        order = PaymentOrder.objects.create(
            user=self.user, product_type=PaymentOrder.ProductType.SUBSCRIPTION,
            plan=plan, amount_irr=100000,
        )
        return UserSubscription.objects.create(
            user=self.user, plan=plan,
            starts_at=timezone.now() - timedelta(days=1),
            ends_at=ends_at, status=UserSubscription.Status.ACTIVE,
            source_order=order,
        )

    def _get_review(self, user, attempt=None):
        self.client.force_authenticate(user=user)
        return self.client.get(
            f"/api/v1/exams/attempts/{(attempt or self.attempt).pk}/review/"
        )

    def test_non_subscriber_receives_public_explanation_but_no_premium_payload(self):
        response = self._get_review(self.user)
        self.assertEqual(response.status_code, 200)
        question = response.data["questions"][0]
        self.assertEqual(question["explanation"], "پاسخ تشریحی عمومی")
        self.assertTrue(question["premium_locked"])
        self.assertIsNone(question["premium_lesson"])
        self.assertNotIn("تله اصلی", str(response.data))

    def test_active_subscriber_receives_published_premium_lesson(self):
        self._grant_subscription(timezone.now() + timedelta(days=10))
        response = self._get_review(self.user)
        self.assertEqual(response.status_code, 200)
        question = response.data["questions"][0]
        self.assertFalse(question["premium_locked"])
        self.assertEqual(
            question["premium_lesson"]["traps_and_techniques"], "تله اصلی"
        )

    def test_expired_subscription_does_not_unlock_lesson(self):
        self._grant_subscription(timezone.now() - timedelta(seconds=1))
        response = self._get_review(self.user)
        self.assertEqual(response.status_code, 200)
        question = response.data["questions"][0]
        self.assertTrue(question["premium_locked"])
        self.assertIsNone(question["premium_lesson"])

    def test_in_progress_attempt_never_returns_review_or_correct_answers(self):
        attempt = self._make_attempt(self.user, ExamAttempt.Status.IN_PROGRESS)
        response = self._get_review(self.user, attempt)
        self.assertEqual(response.status_code, 404)

    def test_user_cannot_review_another_users_attempt(self):
        response = self._get_review(self.other_user)
        self.assertEqual(response.status_code, 404)

    def test_unauthenticated_user_cannot_review(self):
        response = self.client.get(
            f"/api/v1/exams/attempts/{self.attempt.pk}/review/"
        )
        self.assertEqual(response.status_code, 401)
