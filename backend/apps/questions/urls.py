from django.urls import path

from .views import (\n    PublishedQuestionDetailView, PublishedQuestionListView,\n    DesignerQuestionListCreateView, DesignerQuestionDetailView,\n    DesignerQuestionSubmitView, DesignerQuestionRevisionListView,\n)

urlpatterns = [\n    path("designer/", DesignerQuestionListCreateView.as_view(), name="designer-question-list-create"),\n    path("designer/<uuid:question_id>/", DesignerQuestionDetailView.as_view(), name="designer-question-detail"),\n    path("designer/<uuid:question_id>/submit/", DesignerQuestionSubmitView.as_view(), name="designer-question-submit"),\n    path("designer/<uuid:question_id>/revisions/", DesignerQuestionRevisionListView.as_view(), name="designer-question-revisions"),
    path("", PublishedQuestionListView.as_view(), name="published-question-list"),
    path("<uuid:pk>/", PublishedQuestionDetailView.as_view(), name="published-question-detail"),
]
