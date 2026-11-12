from django.urls import path

from .views import PublishedQuestionDetailView, PublishedQuestionListView

urlpatterns = [
    path("", PublishedQuestionListView.as_view(), name="published-question-list"),
    path("<uuid:pk>/", PublishedQuestionDetailView.as_view(), name="published-question-detail"),
]
