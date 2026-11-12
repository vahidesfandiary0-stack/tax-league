from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from .models import Question
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
