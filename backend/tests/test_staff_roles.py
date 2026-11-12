import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from uuid import uuid4
from rest_framework.test import APIClient

from apps.accounts.roles import sync_staff_roles
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


@pytest.mark.django_db
def test_only_payment_role_can_download_private_receipts():
    user_model = get_user_model()
    staff_without_role = user_model.objects.create_user(
        phone_number="09122220006", is_staff=True
    )
    payment_staff = user_model.objects.create_user(
        phone_number="09122220007", is_staff=True
    )
    sync_staff_roles()
    payment_staff.groups.add(Group.objects.get(name="مسئول پرداخت"))
    order_id = uuid4()
    client = APIClient()

    client.force_authenticate(user=staff_without_role)
    denied = client.get(f"/api/v1/payments/staff/orders/{order_id}/receipt/")
    assert denied.status_code == 403

    client.force_authenticate(user=payment_staff)
    not_found = client.get(f"/api/v1/payments/staff/orders/{order_id}/receipt/")
    assert not_found.status_code == 404


@pytest.mark.django_db
def test_non_staff_account_with_group_membership_cannot_use_staff_endpoints():
    user_model = get_user_model()
    regular_user = user_model.objects.create_user(phone_number="09122220008")
    sync_staff_roles()
    regular_user.groups.add(Group.objects.get(name="پشتیبان"))
    client = APIClient()
    client.force_authenticate(user=regular_user)

    listing = client.get("/api/v1/support/tickets/")
    assert listing.status_code == 200
    assert listing.data == []
    status_response = client.patch(
        f"/api/v1/support/tickets/{uuid4()}/status/",
        {"status": "closed"},
        format="json",
    )
    assert status_response.status_code == 403
