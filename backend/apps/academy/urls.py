from django.urls import path

from .views import TutorChatView, TutorConversationListView

urlpatterns = [
    path("tutor/conversations/", TutorConversationListView.as_view(), name="tutor-conversations"),
    path("tutor/chat/", TutorChatView.as_view(), name="tutor-chat"),
]
