from django.db import transaction
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.subscriptions.access import has_active_academy_access

from .models import TutorConversation, TutorMessage
from .serializers import TutorConversationSerializer
from .services import TutorNotConfigured, TutorProviderError, generate_tutor_answer


def require_academy_subscription(user):
    if not has_active_academy_access(user):
        raise PermissionDenied("برای استفاده از مربی هوشمند باید اشتراک فعال آکادمی داشته باشید.")


class PrivateTutorResponseMixin:
    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        response["Cache-Control"] = "private, no-store"
        response["Vary"] = "Authorization"
        return response


class TutorConversationListView(PrivateTutorResponseMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        require_academy_subscription(request.user)
        conversations = TutorConversation.objects.filter(user=request.user).prefetch_related("messages")
        return Response(TutorConversationSerializer(conversations, many=True).data)


class TutorChatView(PrivateTutorResponseMixin, APIView):
    permission_classes = [IsAuthenticated]
    throttle_scope = "tutor_chat"
    max_question_length = 4000

    def post(self, request):
        require_academy_subscription(request.user)
        question = request.data.get("message", "")
        if not isinstance(question, str) or not question.strip():
            raise ValidationError({"message": "متن پرسش الزامی است."})
        question = question.strip()
        if len(question) > self.max_question_length:
            raise ValidationError({"message": "متن پرسش نباید بیشتر از ۴۰۰۰ نویسه باشد."})

        conversation_id = request.data.get("conversation_id")
        conversation = None
        history = []
        if conversation_id:
            try:
                conversation = TutorConversation.objects.get(
                    pk=conversation_id, user=request.user
                )
            except (TutorConversation.DoesNotExist, ValueError, TypeError):
                raise NotFound("گفتگو پیدا نشد.")
            history = list(
                conversation.messages.order_by("-created_at").values("role", "content")[:10]
            )[::-1]

        try:
            answer, citations, confidence = generate_tutor_answer(question, history)
        except TutorNotConfigured as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except TutorProviderError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

        with transaction.atomic():
            if conversation is None:
                conversation = TutorConversation.objects.create(
                    user=request.user,
                    title=question[:160],
                )
            TutorMessage.objects.create(
                conversation=conversation,
                role=TutorMessage.Role.USER,
                content=question,
            )
            reply = TutorMessage.objects.create(
                conversation=conversation,
                role=TutorMessage.Role.ASSISTANT,
                content=answer,
                citations=citations,
                confidence=confidence,
            )
            conversation.save(update_fields=["updated_at"])

        return Response({
            "conversation_id": str(conversation.pk),
            "message": {
                "id": str(reply.pk),
                "role": reply.role,
                "content": reply.content,
                "citations": reply.citations,
                "confidence": reply.confidence,
                "created_at": reply.created_at,
            },
        }, status=status.HTTP_200_OK)
