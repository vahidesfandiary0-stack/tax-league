from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.questions.models import Question, QuestionOption
from apps.questions.services import review_question, submit_for_review


class QuestionWorkflowTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.author = User.objects.create_user(phone_number="09120000001")
        self.reviewer = User.objects.create_user(phone_number="09120000002")
        self.question = Question.objects.create(
            subject=Question.Subject.DIRECT_TAX,
            prompt="نمونه سؤال آزمایشی؟",
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
        self.question.status = Question.Status.PUBLISHED
        self.question.save()
        client = APIClient()
        response = client.get("/api/v1/questions/")
        self.assertEqual(response.status_code, 401)
        self.client = client
        client.force_authenticate(user=self.author)
        response = client.get("/api/v1/questions/")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("is_correct", str(response.data))
