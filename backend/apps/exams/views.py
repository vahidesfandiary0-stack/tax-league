from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Exam, ExamAttempt
from .serializers import (
    AnswerInputSerializer, AttemptSerializer, ExamListSerializer, ResultSerializer,
)
from .services import finalize_attempt, save_answer, start_attempt


def service_error(exc):
    return ValidationError({"detail": exc.messages if hasattr(exc, "messages") else str(exc)})


class ExamListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ExamListSerializer
    queryset = Exam.objects.filter(status=Exam.Status.PUBLISHED).prefetch_related("exam_questions")


class StartAttemptView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, exam_id):
        try:
            attempt = start_attempt(exam_id, request.user)
        except (DjangoValidationError, Exam.DoesNotExist) as exc:
            raise service_error(exc)
        response_status = status.HTTP_200_OK if attempt.questions.exists() and attempt.started_at < __import__("django.utils.timezone", fromlist=["now"]).now() else status.HTTP_201_CREATED
        return Response(AttemptSerializer(attempt).data, status=response_status)


class AnswerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, attempt_id):
        serializer = AnswerInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            save_answer(attempt_id, serializer.validated_data["question_id"], serializer.validated_data["option_id"], request.user)
        except (DjangoValidationError, ExamAttempt.DoesNotExist) as exc:
            raise service_error(exc)
        return Response({"saved": True})


class FinalizeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, attempt_id):
        try:
            attempt = finalize_attempt(attempt_id, request.user)
        except (DjangoValidationError, ExamAttempt.DoesNotExist) as exc:
            raise service_error(exc)
        return Response(ResultSerializer(attempt).data)


class ResultView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ResultSerializer
    lookup_url_kwarg = "attempt_id"

    def get_queryset(self):
        return ExamAttempt.objects.filter(user=self.request.user, status__in=[ExamAttempt.Status.SUBMITTED, ExamAttempt.Status.EXPIRED])
