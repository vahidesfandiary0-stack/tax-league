from django.urls import path

from .views import (
    AnswerView, ExamFocusStatusView, ExamListView, FinalizeView,
    ResultView, StartAttemptView, MyResultsView,
)

urlpatterns = [
    path("", ExamListView.as_view(), name="exam-list"),
    path("focus-status/", ExamFocusStatusView.as_view(), name="exam-focus-status"),
    path("results/", MyResultsView.as_view(), name="my-exam-results"),
    path("<uuid:exam_id>/start/", StartAttemptView.as_view(), name="exam-start"),
    path("attempts/<uuid:attempt_id>/answers/", AnswerView.as_view(), name="attempt-answer"),
    path("attempts/<uuid:attempt_id>/finalize/", FinalizeView.as_view(), name="attempt-finalize"),
    path("attempts/<uuid:attempt_id>/result/", ResultView.as_view(), name="attempt-result"),
]
