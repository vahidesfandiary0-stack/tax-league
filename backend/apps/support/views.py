from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import SupportMessage, SupportTicket
from .serializers import (
    SupportMessageCreateSerializer, SupportTicketCreateSerializer,
    SupportTicketDetailSerializer, SupportTicketListSerializer,
)


class SupportTicketListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = SupportTicket.objects.select_related("user").prefetch_related("messages")
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return SupportTicketCreateSerializer
        return SupportTicketListSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ticket = SupportTicket.objects.create(
            user=request.user,
            subject=serializer.validated_data["subject"],
            category=serializer.validated_data["category"],
        )
        SupportMessage.objects.create(
            ticket=ticket, sender=request.user,
            body=serializer.validated_data["first_message"],
            is_staff_reply=False,
        )
        return Response(
            SupportTicketDetailSerializer(ticket).data,
            status=status.HTTP_201_CREATED,
        )


class SupportTicketDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SupportTicketDetailSerializer
    lookup_url_kwarg = "ticket_id"

    def get_queryset(self):
        queryset = SupportTicket.objects.prefetch_related("messages__sender")
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(user=self.request.user)


class SupportMessageCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, ticket_id):
        queryset = SupportTicket.objects.select_for_update()
        if not request.user.is_staff:
            queryset = queryset.filter(user=request.user)
        ticket = get_object_or_404(queryset, pk=ticket_id)
        if ticket.status == SupportTicket.Status.CLOSED:
            raise ValidationError("این درخواست بسته شده و امکان ارسال پیام ندارد.")
        serializer = SupportMessageCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        is_staff_reply = bool(request.user.is_staff)
        SupportMessage.objects.create(
            ticket=ticket, sender=request.user,
            body=serializer.validated_data["body"],
            is_staff_reply=is_staff_reply,
        )
        ticket.status = (
            SupportTicket.Status.WAITING_USER if is_staff_reply
            else SupportTicket.Status.IN_PROGRESS
        )
        ticket.save(update_fields=["status", "updated_at"])
        ticket.refresh_from_db()
        return Response(SupportTicketDetailSerializer(ticket).data, status=status.HTTP_201_CREATED)


class SupportTicketStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, ticket_id):
        if not request.user.is_staff:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("فقط پشتیبانی مجاز به تغییر وضعیت است.")
        ticket = get_object_or_404(SupportTicket, pk=ticket_id)
        new_status = request.data.get("status")
        valid = {choice for choice, _ in SupportTicket.Status.choices}
        if new_status not in valid:
            raise ValidationError({"status": "وضعیت انتخاب‌شده معتبر نیست."})
        ticket.status = new_status
        ticket.save(update_fields=["status", "updated_at"])
        return Response(SupportTicketDetailSerializer(ticket).data)
