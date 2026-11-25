from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.subscriptions.models import UserSubscription
from .models import AcademyContent
from .serializers import AcademyContentDetailSerializer, AcademyContentListSerializer


def has_active_subscription(user):
    now = timezone.now()
    return UserSubscription.objects.filter(
        user=user,
        status=UserSubscription.Status.ACTIVE,
        starts_at__lte=now,
        ends_at__gt=now,
    ).exists()


class AcademyContentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        active = has_active_subscription(request.user)
        queryset = AcademyContent.objects.filter(is_active=True)
        serializer = AcademyContentListSerializer(
            queryset, many=True, context={"has_subscription": active}
        )
        return Response({
            "has_active_subscription": active,
            "results": serializer.data,
        })


class AcademyContentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug):
        content = get_object_or_404(AcademyContent, slug=slug, is_active=True)
        if content.is_exclusive and not has_active_subscription(request.user):
            raise PermissionDenied("برای مشاهده این محتوای اختصاصی، اشتراک فعال لازم است.")
        return Response(AcademyContentDetailSerializer(content).data)
