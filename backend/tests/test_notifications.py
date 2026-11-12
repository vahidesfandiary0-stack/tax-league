import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.notifications.models import Notification


@pytest.mark.django_db
def test_user_sees_only_own_notifications_and_can_mark_read():
    user_model = get_user_model()
    owner = user_model.objects.create_user(phone_number="09120000001")
    other = user_model.objects.create_user(phone_number="09120000002")
    own = Notification.objects.create(
        recipient=owner, kind=Notification.Kind.EXAM_RESULT,
        title="نتیجه آزمون", body="نتیجه ثبت شد.",
    )
    Notification.objects.create(
        recipient=other, kind=Notification.Kind.PAYMENT_APPROVED,
        title="پرداخت", body="پرداخت تأیید شد.",
    )

    client = APIClient()
    client.force_authenticate(user=owner)
    response = client.get("/api/v1/notifications/")
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["id"] == own.pk
    assert response.data[0]["is_read"] is False

    read_response = client.post(f"/api/v1/notifications/{own.pk}/read/")
    assert read_response.status_code == 200
    assert read_response.data["is_read"] is True


@pytest.mark.django_db
def test_user_cannot_mark_another_users_notification_read():
    user_model = get_user_model()
    owner = user_model.objects.create_user(phone_number="09120000003")
    stranger = user_model.objects.create_user(phone_number="09120000004")
    notification = Notification.objects.create(
        recipient=owner, kind=Notification.Kind.PAYMENT_REJECTED,
        title="پرداخت", body="رسید تأیید نشد.",
    )

    client = APIClient()
    client.force_authenticate(user=stranger)
    response = client.post(f"/api/v1/notifications/{notification.pk}/read/")
    assert response.status_code == 404
    notification.refresh_from_db()
    assert notification.read_at is None
