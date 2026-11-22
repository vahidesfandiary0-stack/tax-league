from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from .models import Question, QuestionRevision
from .serializers import PublicQuestionSerializer


class PublishedQuestionQuerysetMixin:
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Question.objects.filter(status=Question.Status.PUBLISHED).prefetch_related("options")


class PublishedQuestionListView(PublishedQuestionQuerysetMixin, ListAPIView):
    serializer_class = PublicQuestionSerializer
    filterset_fields = ["subject", "difficulty"]


class PublishedQuestionDetailView(PublishedQuestionQuerysetMixin, RetrieveAPIView):
    serializer_class = PublicQuestionSerializer


from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError as APIValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import DesignerQuestionSerializer, QuestionRevisionSerializer
from .services import submit_for_review


class DesignerQuestionListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DesignerQuestionSerializer

    def get_queryset(self):
        return Question.objects.filter(author=self.request.user).prefetch_related("options", "revisions")


class DesignerQuestionDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DesignerQuestionSerializer
    lookup_url_kwarg = "question_id"

    def get_queryset(self):
        return Question.objects.filter(author=self.request.user).prefetch_related("options", "revisions")


class DesignerQuestionSubmitView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, question_id):
        question = get_object_or_404(Question, pk=question_id, author=request.user)
        try:
            question = submit_for_review(question.pk, request.user)
        except Exception as exc:
            raise APIValidationError(str(exc)) from exc
        return Response(DesignerQuestionSerializer(question).data, status=status.HTTP_200_OK)


class DesignerQuestionRevisionListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = QuestionRevisionSerializer

    def get_queryset(self):
        return QuestionRevision.objects.filter(question__author=self.request.user, question_id=self.kwargs["question_id"]).select_related("changed_by")
