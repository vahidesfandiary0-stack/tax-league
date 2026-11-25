from django.urls import path

from .views import NotificationListView, NotificationMarkReadView, ShowcaseSlideListView

urlpatterns = [
    path("", NotificationListView.as_view(), name="notification-list"),
    path("showcase/", ShowcaseSlideListView.as_view(), name="notification-showcase"),
    path("<int:notification_id>/read/", NotificationMarkReadView.as_view(), name="notification-mark-read"),
]
