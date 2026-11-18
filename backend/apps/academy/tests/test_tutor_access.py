from datetime import timedelta
from unittest.mock import patch

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.academy.models import TutorConversation
from apps.payments.models import PaymentOrder
from apps.subscriptions.models import SubscriptionPlan, UserSubscription
from apps.academy.services import TutorNotConfigured


@pytest.mark.django_db
def test_tutor_chat_is_blocked_without_active_subscription():
    user = User.objects.create_user("09120000101")
    client = APIClient()
    client.force_authenticate(user=user)

    with patch("apps.academy.views.generate_tutor_answer") as generate:
        response = client.post(
            "/api/v1/academy/tutor/chat/",
            {"message": "سؤال مالیاتی"},
            format="json",
        )

    assert response.status_code == 403
    generate.assert_not_called()


@pytest.mark.django_db
def test_active_subscriber_can_use_tutor_and_receive_citations():
    user = User.objects.create_user("09120000102")
    plan = SubscriptionPlan.objects.create(
        title="طرح آزمایشی", period=SubscriptionPlan.Period.MONTHLY,
        duration_days=30, price_irr=100000,
    )
    order = PaymentOrder.objects.create(
        user=user, product_type=PaymentOrder.ProductType.SUBSCRIPTION,
        plan=plan, amount_irr=100000,
    )
    UserSubscription.objects.create(
        user=user, plan=plan,
        starts_at=timezone.now() - timedelta(days=1),
        ends_at=timezone.now() + timedelta(days=10),
        status=UserSubscription.Status.ACTIVE,
        source_order=order,
    )
    client = APIClient()
    client.force_authenticate(user=user)

    with patch(
        "apps.academy.views.generate_tutor_answer",
        return_value=("پاسخ مستند", [{"id": "S1", "title": "قانون نمونه"}], "medium"),
    ):
        response = client.post(
            "/api/v1/academy/tutor/chat/",
            {"message": "سؤال مالیاتی"},
            format="json",
        )

    assert response.status_code == 200
    assert response.data["message"]["content"] == "پاسخ مستند"
    assert response.data["message"]["citations"][0]["id"] == "S1"
    conversation = TutorConversation.objects.get(user=user)
    assert conversation.messages.count() == 2


@pytest.mark.django_db
def test_tutor_provider_unconfigured_returns_service_unavailable():
    user = User.objects.create_user("09120000103")
    plan = SubscriptionPlan.objects.create(
        title="طرح آزمایشی", period=SubscriptionPlan.Period.MONTHLY,
        duration_days=30, price_irr=100000,
    )
    order = PaymentOrder.objects.create(
        user=user, product_type=PaymentOrder.ProductType.SUBSCRIPTION,
        plan=plan, amount_irr=100000,
    )
    UserSubscription.objects.create(
        user=user, plan=plan,
        starts_at=timezone.now() - timedelta(days=1),
        ends_at=timezone.now() + timedelta(days=10),
        status=UserSubscription.Status.ACTIVE,
        source_order=order,
    )
    client = APIClient()
    client.force_authenticate(user=user)

    with patch(
        "apps.academy.views.generate_tutor_answer",
        side_effect=TutorNotConfigured("provider not configured"),
    ):
        response = client.post(
            "/api/v1/academy/tutor/chat/",
            {"message": "سؤال مالیاتی"},
            format="json",
        )

    assert response.status_code == 503
    assert TutorConversation.objects.filter(user=user).count() == 0


@pytest.mark.django_db
def test_tutor_conversation_history_is_hidden_without_subscription():
    user = User.objects.create_user("09120000104")
    owner = User.objects.create_user("09120000105")
    TutorConversation.objects.create(user=owner, title="گفتگوی خصوصی")
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get("/api/v1/academy/tutor/conversations/")

    assert response.status_code == 403
