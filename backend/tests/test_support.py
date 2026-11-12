import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.notifications.models import Notification
from apps.support.models import SupportTicket


@pytest.mark.django_db
def test_customer_can_create_and_read_own_support_ticket():
    user_model = get_user_model()
    owner = user_model.objects.create_user(phone_number="09121110001", display_name="آزمون")
    stranger = user_model.objects.create_user(phone_number="09121110002")
    client = APIClient()
    client.force_authenticate(user=owner)

    created = client.post("/api/v1/support/tickets/", {
        "subject": "مشکل ورود",
        "category": "account",
        "first_message": "برای ورود به حساب مشکل دارم.",
    }, format="json")
    assert created.status_code == 201
    ticket_id = created.data["id"]
    assert len(created.data["messages"]) == 1
    assert "sender" not in created.data["messages"][0]

    client.force_authenticate(user=stranger)
    forbidden = client.get(f"/api/v1/support/tickets/{ticket_id}/")
    assert forbidden.status_code == 404


@pytest.mark.django_db
def test_staff_reply_creates_private_in_app_notification():
    user_model = get_user_model()
    owner = user_model.objects.create_user(phone_number="09121110003")
    staff = user_model.objects.create_user(phone_number="09121110004", is_staff=True)
    ticket = SupportTicket.objects.create(
        user=owner, subject="سؤال درباره آزمون",
        category=SupportTicket.Category.EXAM,
    )
    client = APIClient()
    client.force_authenticate(user=staff)
    response = client.post(
        f"/api/v1/support/tickets/{ticket.pk}/messages/",
        {"body": "درخواست شما بررسی شد."},
        format="json",
    )
    assert response.status_code == 201
    assert response.data["messages"][-1]["sender_label"] == "پشتیبانی"
    assert Notification.objects.filter(
        recipient=owner, kind=Notification.Kind.SUPPORT_REPLY,
        data__ticket_id=str(ticket.pk),
    ).exists()


@pytest.mark.django_db
def test_customer_cannot_change_ticket_status():
    user_model = get_user_model()
    owner = user_model.objects.create_user(phone_number="09121110005")
    ticket = SupportTicket.objects.create(user=owner, subject="درخواست", category="other")
    client = APIClient()
    client.force_authenticate(user=owner)
    response = client.patch(
        f"/api/v1/support/tickets/{ticket.pk}/status/",
        {"status": SupportTicket.Status.CLOSED},
        format="json",
    )
    assert response.status_code == 403
    ticket.refresh_from_db()
    assert ticket.status == SupportTicket.Status.OPEN
