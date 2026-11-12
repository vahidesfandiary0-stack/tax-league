from django.utils import timezone
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)[:100]


class NotificationMarkReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, notification_id):
        updated = Notification.objects.filter(
            pk=notification_id, recipient=request.user, read_at__isnull=True
        ).update(read_at=timezone.now())
        if not updated:
            exists = Notification.objects.filter(pk=notification_id, recipient=request.user).exists()
            if not exists:
                from rest_framework.exceptions import NotFound
                raise NotFound("اعلان پیدا نشد.")
        notification = Notification.objects.get(pk=notification_id, recipient=request.user)
        return Response(NotificationSerializer(notification).data)
