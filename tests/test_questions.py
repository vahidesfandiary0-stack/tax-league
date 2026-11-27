from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.questions.models import Question, QuestionOption
from apps.questions.services import review_question, submit_for_review, publish_question


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



class DesignerQuestionApiTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.author = User.objects.create_user(phone_number="09120000011")
        self.other = User.objects.create_user(phone_number="09120000012")
        self.reviewer = User.objects.create_user(phone_number="09120000013", is_staff=True)
        self.owner = User.objects.create_superuser(phone_number="09120000014", password="test-password")
        self.client = APIClient()
        self.client.force_authenticate(user=self.author)
        self.payload = {
            "subject": "direct_tax",
            "difficulty": "very_hard",
            "prompt": "در فرض مستقل آزمون، کدام حکم مالیاتی صحیح است؟",
            "explanation": "استدلال مستند پاسخ صحیح در این بخش درج شده است.",
            "source_reference": "قانون مالیات‌های مستقیم، ماده نمونه؛ regulation.tax.gov.ir",
            "options": [
                {"position": 1, "text": "گزینه نخست", "is_correct": False},
                {"position": 2, "text": "گزینه دوم", "is_correct": True},
                {"position": 3, "text": "گزینه سوم", "is_correct": False},
                {"position": 4, "text": "گزینه چهارم", "is_correct": False},
            ],
        }

    def test_designer_can_create_draft_and_revision_is_recorded(self):
        response = self.client.post("/api/v1/questions/designer/", self.payload, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["status"], Question.Status.DRAFT)
        question = Question.objects.get(pk=response.data["id"])
        self.assertEqual(question.revisions.count(), 1)
        self.assertEqual(question.revisions.first().snapshot["options"][1]["is_correct"], True)

    def test_designer_questions_are_private_to_author(self):
        response = self.client.post("/api/v1/questions/designer/", self.payload, format="json")
        question_id = response.data["id"]
        self.client.force_authenticate(user=self.other)
        self.assertEqual(self.client.get("/api/v1/questions/designer/").data, [])
        self.assertEqual(self.client.get(f"/api/v1/questions/designer/{question_id}/").status_code, 404)

    def test_submit_locks_question_for_review_and_owner_controls_publication(self):
        response = self.client.post("/api/v1/questions/designer/", self.payload, format="json")
        question_id = response.data["id"]
        submitted = self.client.post(f"/api/v1/questions/designer/{question_id}/submit/", {}, format="json")
        self.assertEqual(submitted.status_code, 200)
        self.assertEqual(submitted.data["status"], Question.Status.PENDING)
        self.client.force_authenticate(user=self.reviewer)
        with self.assertRaises(Exception):
            publish_question(question_id, self.reviewer)
        review_question(question_id, self.reviewer, True, "تأیید علمی بازبین")
        with self.assertRaises(Exception):
            publish_question(question_id, self.reviewer)
        published = publish_question(question_id, self.owner)
        self.assertEqual(published.status, Question.Status.PUBLISHED)

    def test_owner_can_publish_complete_draft_without_second_reviewer(self):
        response = self.client.post("/api/v1/questions/designer/", self.payload, format="json")
        self.assertEqual(response.status_code, 201)
        question = Question.objects.get(pk=response.data["id"])

        published = publish_question(question.pk, self.owner)

        self.assertEqual(published.status, Question.Status.PUBLISHED)
        self.assertIsNone(published.reviewer_id)
        self.assertEqual(published.review_decision, "owner_published")

    def test_owner_publication_preserves_rejection_feedback(self):
        response = self.client.post(
            "/api/v1/questions/designer/", self.payload, format="json"
        )
        question = Question.objects.get(pk=response.data["id"])
        rejection_feedback = "بازبین: استدلال حقوقی سؤال نیازمند اصلاح است."
        question.status = Question.Status.REJECTED
        question.review_decision = "rejected"
        question.review_reason = rejection_feedback
        question.save(update_fields=[
            "status", "review_decision", "review_reason"
        ])

        published = publish_question(question.pk, self.owner)

        self.assertEqual(published.status, Question.Status.PUBLISHED)
        self.assertEqual(published.review_decision, "owner_published")
        self.assertEqual(published.review_reason, rejection_feedback)

    def test_non_owner_cannot_publish_draft_directly(self):
        response = self.client.post("/api/v1/questions/designer/", self.payload, format="json")
        question = Question.objects.get(pk=response.data["id"])

        with self.assertRaises(Exception):
            publish_question(question.pk, self.reviewer)

    def test_submission_requires_exactly_four_options_and_one_correct(self):
        invalid = dict(self.payload)
        invalid["options"] = invalid["options"][:3]
        response = self.client.post("/api/v1/questions/designer/", invalid, format="json")
        self.assertEqual(response.status_code, 400)
