import uuid
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models


def receipt_upload_path(instance, filename):
    suffix = Path(filename).suffix.lower()
    return f"private-payment-receipts/{instance.id}/{uuid.uuid4().hex}{suffix}"


def validate_receipt_size(file_obj):
    if file_obj.size > 5 * 1024 * 1024:
        raise ValidationError("حجم رسید نباید بیشتر از ۵ مگابایت باشد.")


class PaymentSettings(models.Model):
    """Singleton-like admin-managed bank transfer configuration; never expose via public serializers."""
    card_number = models.CharField(max_length=32, blank=True)
    account_holder = models.CharField(max_length=120, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("تنظیمات پرداخت قابل حذف نیست.")

    def __str__(self):
        return "تنظیمات کارت‌به‌کارت"


class PaymentOrder(models.Model):
    class ProductType(models.TextChoices):
        SUBSCRIPTION = "subscription", "اشتراک"
        EXAM = "exam", "خرید آزمون"

    class Status(models.TextChoices):
        AWAITING_PAYMENT = "awaiting_payment", "در انتظار پرداخت"
        UNDER_REVIEW = "under_review", "در انتظار بررسی"
        APPROVED = "approved", "تأییدشده"
        REJECTED = "rejected", "ردشده"
        CANCELLED = "cancelled", "لغوشده"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="payment_orders")
    product_type = models.CharField(max_length=16, choices=ProductType.choices)
    plan = models.ForeignKey("subscriptions.SubscriptionPlan", null=True, blank=True, on_delete=models.PROTECT)
    exam = models.ForeignKey("exams.Exam", null=True, blank=True, on_delete=models.PROTECT)
    amount_irr = models.PositiveBigIntegerField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AWAITING_PAYMENT)
    tracking_code = models.CharField(max_length=100, blank=True)
    receipt = models.FileField(
        upload_to=receipt_upload_path,
        validators=[FileExtensionValidator(["jpg", "jpeg", "png", "pdf"]), validate_receipt_size],
        blank=True,
    )
    user_note = models.CharField(max_length=500, blank=True)
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, related_name="reviewed_payment_orders")
    review_note = models.CharField(max_length=500, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "status"])]

    def clean(self):
        if self.amount_irr < 1:
            raise ValidationError({"amount_irr": "مبلغ سفارش باید بیشتر از صفر باشد."})
        if self.product_type == self.ProductType.SUBSCRIPTION and (not self.plan_id or self.exam_id):
            raise ValidationError("سفارش اشتراک باید فقط یک طرح اشتراک داشته باشد.")
        if self.product_type == self.ProductType.EXAM and (not self.exam_id or self.plan_id):
            raise ValidationError("سفارش آزمون باید فقط یک آزمون داشته باشد.")

    def save(self, *args, **kwargs):
        if self.pk:
            old = PaymentOrder.objects.get(pk=self.pk)
            immutable = ("user_id", "product_type", "plan_id", "exam_id", "amount_irr")
            if any(getattr(old, field) != getattr(self, field) for field in immutable):
                raise ValidationError("مشخصات و مبلغ سفارش پس از ایجاد قابل تغییر نیست.")
            if old.status == self.Status.APPROVED:
                if self.status != old.status or self.receipt != old.receipt:
                    raise ValidationError("سفارش تأییدشده قابل تغییر نیست.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.id} · {self.amount_irr:,} ریال"
