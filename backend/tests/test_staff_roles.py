import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APIClient

from apps.accounts.roles import ROLE_PERMISSIONS, sync_staff_roles
from apps.support.models import SupportTicket


@pytest.mark.django_db
def test_role_sync_creates_separate_least_privilege_groups():
    sync_staff_roles()
    payment_group = Group.objects.get(name="مسئول پرداخت")
    support_group = Group.objects.get(name="پشتیبان")

    assert payment_group.permissions.filter(codename="change_paymentorder").exists()
    assert not payment_group.permissions.filter(codename="change_supportticket").exists()
    assert support_group.permissions.filter(codename="change_supportticket").exists()
    assert not support_group.permissions.filter(codename="change_paymentorder").exists()


@pytest.mark.django_db
def test_staff_without_support_role_cannot_access_all_tickets_or_change_status():
    user_model = get_user_model()
    customer = user_model.objects.create_user(phone_number="09122220001")
    other_customer = user_model.objects.create_user(phone_number="09122220002")
    unprivileged_staff = user_model.objects.create_user(
        phone_number="09122220003", is_staff=True
    )
    own_ticket = SupportTicket.objects.create(
        user=unprivileged_staff, subject="درخواست شخصی", category="other"
    )
    SupportTicket.objects.create(
        user=customer, subject="درخواست مشتری", category="other"
    )

    client = APIClient()
    client.force_authenticate(user=unprivileged_staff)
    listing = client.get("/api/v1/support/tickets/")
    assert listing.status_code == 200
    assert len(listing.data) == 1
    assert listing.data[0]["id"] == str(own_ticket.pk)

    response = client.patch(
        f"/api/v1/support/tickets/{own_ticket.pk}/status/",
        {"status": SupportTicket.Status.CLOSED},
        format="json",
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_staff_roles_do_not_receive_user_or_payment_settings_permissions():
    sync_staff_roles()
    payment_group = Group.objects.get(name="مسئول پرداخت")
    support_group = Group.objects.get(name="پشتیبان")
    assert not payment_group.permissions.filter(codename__in=[
        "change_user", "add_user", "delete_user", "change_paymentsettings"
    ]).exists()
    assert not support_group.permissions.filter(codename__in=[
        "change_user", "add_user", "delete_user", "change_paymentsettings"
    ]).exists()
