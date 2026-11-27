import mimetypes
from pathlib import Path

from django.conf import settings
from django.db.models import Q
from django.http import FileResponse, Http404
from django.utils import timezone
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.exams.models import Exam

from .models import Notification, ShowcaseSlide
from .serializers import NotificationSerializer


def showcase_image(request, path):
    root = (Path(settings.MEDIA_ROOT) / "showcase").resolve()
    target = (root / path).resolve()
    try:
        target.relative_to(root)
    except ValueError:
        raise Http404
    if not target.is_file() or target.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
        raise Http404
    return FileResponse(
        target.open("rb"),
        content_type=mimetypes.guess_type(target.name)[0] or "application/octet-stream",
    )


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


class ShowcaseSlideListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        now = timezone.now()
        next_exam = Exam.objects.filter(
            status=Exam.Status.PUBLISHED,
            counts_for_league=True,
            starts_at__gt=now,
        ).filter(
            Q(ends_at__isnull=True) | Q(ends_at__gt=now)
        ).order_by("starts_at", "pk").first()

        slides = ShowcaseSlide.objects.filter(is_active=True).filter(
            Q(starts_at__isnull=True) | Q(starts_at__lte=now),
            Q(ends_at__isnull=True) | Q(ends_at__gt=now),
        ).order_by("sort_order", "pk")

        result = []
        for slide in slides:
            if slide.kind == ShowcaseSlide.Kind.EXAM_COUNTDOWN and next_exam is None:
                continue
            item = {
                "id": slide.pk,
                "kind": slide.kind,
                "title": slide.title,
                "body": slide.body,
                "image_url": request.build_absolute_uri("/" + slide.image.url.lstrip("/")) if slide.image else slide.image_url,
                "duration_seconds": slide.duration_seconds,
            }
            if slide.kind == ShowcaseSlide.Kind.EXAM_COUNTDOWN:
                item["starts_at"] = next_exam.starts_at
                item["exam_title"] = next_exam.title
            result.append(item)
        return Response(result)
