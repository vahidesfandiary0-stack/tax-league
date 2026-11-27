from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from apps.accounts.models import User
from apps.exams.models import Exam
from apps.exams.views import ExamListView


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
