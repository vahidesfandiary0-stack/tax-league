from django.urls import path

from .views import (
    PublishedQuestionDetailView, PublishedQuestionListView,
    DesignerQuestionListCreateView, DesignerQuestionDetailView,
    DesignerQuestionSubmitView, DesignerQuestionRevisionListView,
)

urlpatterns = [
    path("designer/", DesignerQuestionListCreateView.as_view(), name="designer-question-list-create"),
    path("designer/<uuid:question_id>/", DesignerQuestionDetailView.as_view(), name="designer-question-detail"),
    path("designer/<uuid:question_id>/submit/", DesignerQuestionSubmitView.as_view(), name="designer-question-submit"),
    path("designer/<uuid:question_id>/revisions/", DesignerQuestionRevisionListView.as_view(), name="designer-question-revisions"),
    path("", PublishedQuestionListView.as_view(), name="published-question-list"),
    path("<uuid:pk>/", PublishedQuestionDetailView.as_view(), name="published-question-detail"),
]
