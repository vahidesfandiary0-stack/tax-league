from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.questions.models import Question, QuestionOption
from apps.questions.services import (publish_question, review_question, submit_for_review, verify_question_source)


class QuestionWorkflowTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.author = User.objects.create_user(phone_number="09120000001")
        self.reviewer = User.objects.create_user(phone_number="09120000002")
        self.question = Question.objects.create(
            subject=Question.Subject.DIRECT_TAX,
            difficulty=Question.Difficulty.HARD,
            prompt="نمونه سؤال آزمایشی؟",
            explanation="پاسخ تشریحی مستند آزمایشی.",
            source_reference="قانون آزمایشی، ماده ۱",
            author=self.author,
        )
        for position in range(1, 5):
            QuestionOption.objects.create(
                question=self.question,
                position=position,
                text=f"گزینه {position}",
                is_correct=(position == 2),
            )

    def test_author_cannot_review_own_question(self):
        submit_for_review(self.question.pk, self.author)
        with self.assertRaises(Exception):
            review_question(self.question.pk, self.author, True)

    def test_public_api_never_exposes_correct_answer(self):
        submit_for_review(self.question.pk, self.author)
        review_question(self.question.pk, self.reviewer, True)
        verify_question_source(self.question.pk, self.reviewer)
        publish_question(self.question.pk)
        client = APIClient()
        response = client.get("/api/v1/questions/")
        self.assertEqual(response.status_code, 401)
        self.client = client
        client.force_authenticate(user=self.author)
        response = client.get("/api/v1/questions/")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("is_correct", str(response.data))

    def test_question_cannot_be_published_without_separate_official_source_verification(self):
        submit_for_review(self.question.pk, self.author)
        review_question(self.question.pk, self.reviewer, True)
        with self.assertRaises(Exception):
            publish_question(self.question.pk)
        verify_question_source(self.question.pk, self.reviewer)
        published = publish_question(self.question.pk)
        self.assertEqual(published.status, Question.Status.PUBLISHED)
        self.assertEqual(published.source_verified_by_id, self.reviewer.pk)

    def test_medium_question_cannot_be_approved_for_official_exams(self):
        self.question.difficulty = Question.Difficulty.MEDIUM
        self.question.save(update_fields=["difficulty"])
        submit_for_review(self.question.pk, self.author)
        with self.assertRaises(Exception):
            review_question(self.question.pk, self.reviewer, True)

    def test_published_question_cannot_be_created_or_promoted_directly(self):
        with self.assertRaises(Exception):
            Question.objects.create(
                subject=Question.Subject.DIRECT_TAX,
                difficulty=Question.Difficulty.HARD,
                prompt="انتشار مستقیم",
                author=self.author,
                status=Question.Status.PUBLISHED,
            )
        submit_for_review(self.question.pk, self.author)
        review_question(self.question.pk, self.reviewer, True)
        verify_question_source(self.question.pk, self.reviewer)
        self.question.refresh_from_db()
        self.question.status = Question.Status.PUBLISHED
        with self.assertRaises(Exception):
            self.question.save()

