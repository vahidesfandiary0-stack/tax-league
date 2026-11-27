from django.test import TestCase
from rest_framework.test import APIClient, APIRequestFactory, force_authenticate

from apps.accounts.models import User
from apps.exams.models import Exam, ExamAttempt, ExamQuestion
from apps.exams.views import ExamListView
from apps.league.models import LeagueScoreEntry
from apps.questions.models import Question, QuestionOption


class PublicDemoExamVisibilityTests(TestCase):
    def setUp(self):
        self.first_user = User.objects.create_user("+989120000011")
        self.second_user = User.objects.create_user("+989120000012")
        self.public_demo_exam = Exam.objects.create(
            title="آزمون آزمایشی عمومی",
            kind=Exam.Kind.MOCK,
            status=Exam.Status.PUBLISHED,
            counts_for_league=False,
            requires_purchase=False,
            test_user=None,
        )
        self.factory = APIRequestFactory()

    def test_public_demo_exam_is_listed_for_every_authenticated_user(self):
        for user in (self.first_user, self.second_user):
            request = self.factory.get("/api/v1/exams/")
            force_authenticate(request, user=user)
            response = ExamListView.as_view()(request)
            exam_ids = {item["id"] for item in response.data}
            self.assertIn(str(self.public_demo_exam.pk), exam_ids)

    def test_demo_exam_is_not_configured_to_affect_league(self):
        self.assertIsNone(self.public_demo_exam.test_user_id)
        self.assertFalse(self.public_demo_exam.counts_for_league)
        self.assertFalse(self.public_demo_exam.requires_purchase)

    def test_mock_exam_full_flow_saves_result_without_league_entry(self):
        user = User.objects.create_user("+989120000013")
        question = Question.objects.create(
            subject=Question.Subject.DIRECT_TAX,
            difficulty=Question.Difficulty.EASY,
            prompt="سؤال آزمایشی",
            explanation="توضیح پاسخ آزمایشی",
            status=Question.Status.DRAFT,
            author=user,
        )
        correct_option = None
        for position in range(1, 5):
            option = QuestionOption.objects.create(
                question=question,
                position=position,
                text=f"گزینه {position}",
                is_correct=(position == 2),
            )
            if option.is_correct:
                correct_option = option

        question.status = Question.Status.PUBLISHED
        question.save(update_fields=["status"])

        exam = Exam.objects.create(
            title="آزمون آزمایشی جریان کامل",
            kind=Exam.Kind.MOCK,
            status=Exam.Status.PUBLISHED,
            duration_minutes=10,
            max_attempts=20,
            counts_for_league=False,
            requires_purchase=False,
            test_user=None,
        )
        ExamQuestion.objects.create(
            exam=exam,
            question=question,
            position=1,
            points_correct=10,
            points_wrong=0,
        )

        client = APIClient()
        client.force_authenticate(user=user)

        start = client.post(f"/api/v1/exams/{exam.pk}/start/", {}, format="json")
        self.assertEqual(start.status_code, 200)
        attempt_id = start.data["id"]
        attempt_question = start.data["questions"][0]
        attempt_option = ExamAttempt.objects.get(pk=attempt_id).questions.get().options.get(
            source_option_id=correct_option.pk
        )

        answer = client.post(
            f"/api/v1/exams/attempts/{attempt_id}/answers/",
            {"question_id": attempt_question["id"], "option_id": attempt_option.pk},
            format="json",
        )
        self.assertEqual(answer.status_code, 200)
        self.assertTrue(answer.data["saved"])

        finalize = client.post(
            f"/api/v1/exams/attempts/{attempt_id}/finalize/",
            {},
            format="json",
        )
        self.assertEqual(finalize.status_code, 200)
        self.assertEqual(finalize.data["status"], ExamAttempt.Status.SUBMITTED)
        self.assertEqual(finalize.data["score"], 10)
        self.assertEqual(finalize.data["correct_count"], 1)
        self.assertEqual(finalize.data["wrong_count"], 0)
        self.assertEqual(finalize.data["blank_count"], 0)

        result = client.get(f"/api/v1/exams/attempts/{attempt_id}/result/")
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.data["score"], 10)

        history = client.get("/api/v1/exams/results/")
        self.assertEqual(history.status_code, 200)
        self.assertEqual(len(history.data), 1)
        self.assertEqual(history.data[0]["exam_title"], exam.title)
        self.assertFalse(history.data[0]["counts_for_league"])

        self.assertFalse(LeagueScoreEntry.objects.filter(attempt_id=attempt_id).exists())
