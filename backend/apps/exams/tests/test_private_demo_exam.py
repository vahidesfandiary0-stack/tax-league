from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from apps.accounts.models import User
from apps.exams.models import Exam
from apps.exams.views import ExamListView, StartAttemptView


class PrivateDemoExamVisibilityTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user("+989120000011")
        self.other = User.objects.create_user("+989120000012")
        self.private_exam = Exam.objects.create(
            title="آزمون آزمایشی شخصی",
            kind=Exam.Kind.MOCK,
            status=Exam.Status.PUBLISHED,
            counts_for_league=False,
            test_user=self.owner,
        )
        self.public_exam = Exam.objects.create(
            title="آزمون عمومی",
            kind=Exam.Kind.MOCK,
            status=Exam.Status.PUBLISHED,
            counts_for_league=False,
        )
        self.factory = APIRequestFactory()

    def test_private_exam_is_listed_only_for_its_owner(self):
        owner_request = self.factory.get("/api/v1/exams/")
        force_authenticate(owner_request, user=self.owner)
        owner_response = ExamListView.as_view()(owner_request)
        owner_ids = {item["id"] for item in owner_response.data}
        self.assertIn(str(self.private_exam.pk), owner_ids)
        self.assertIn(str(self.public_exam.pk), owner_ids)

        other_request = self.factory.get("/api/v1/exams/")
        force_authenticate(other_request, user=self.other)
        other_response = ExamListView.as_view()(other_request)
        other_ids = {item["id"] for item in other_response.data}
        self.assertNotIn(str(self.private_exam.pk), other_ids)
        self.assertIn(str(self.public_exam.pk), other_ids)

    def test_other_user_cannot_start_private_exam_by_guessing_id(self):
        request = self.factory.post(f"/api/v1/exams/{self.private_exam.pk}/start/")
        force_authenticate(request, user=self.other)
        response = StartAttemptView.as_view()(request, exam_id=self.private_exam.pk)
        self.assertEqual(response.status_code, 400)
