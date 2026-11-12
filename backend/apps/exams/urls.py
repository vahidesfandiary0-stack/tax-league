from django.urls import path

from .views import AnswerView, ExamListView, FinalizeView, ResultView, StartAttemptView

urlpatterns = [
    path("", ExamListView.as_view(), name="exam-list"),
    path("<uuid:exam_id>/start/", StartAttemptView.as_view(), name="exam-start"),
    path("attempts/<uuid:attempt_id>/answers/", AnswerView.as_view(), name="attempt-answer"),
    path("attempts/<uuid:attempt_id>/finalize/", FinalizeView.as_view(), name="attempt-finalize"),
    path("attempts/<uuid:attempt_id>/result/", ResultView.as_view(), name="attempt-result"),
]
