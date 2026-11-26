import uuid
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from PIL import Image, UnidentifiedImageError


def receipt_upload_path(instance, filename):
    suffix = Path(filename).suffix.lower()
    return f"private-payment-receipts/{instance.id}/{uuid.uuid4().hex}{suffix}"


def validate_receipt_size(file_obj):
    if file_obj.size > 5 * 1024 * 1024:
        raise ValidationError("حجم رسید نباید بیشتر از ۵ مگابایت باشد.")


def validate_receipt_content(file_obj):
    suffix = Path(getattr(file_obj, "name", "")).suffix.lower()
    file_obj.seek(0)
    head = file_obj.read(8)
    if suffix in {".jpg", ".jpeg", ".png"}:
        try:
            file_obj.seek(0)
            with Image.open(file_obj) as image:
                width, height = image.size
                if width < 1 or height < 1 or width * height > 40_000_000:
                    raise ValidationError("ابعاد تصویر رسید معتبر نیست یا بیش از حد بزرگ است.")
                image.verify()
        except (UnidentifiedImageError, Image.DecompressionBombError, OSError, SyntaxError, ValueError):
            raise ValidationError("فایل تصویر رسید خراب یا نامعتبر است.")
        finally:
            file_obj.seek(0)
        if suffix in {".jpg", ".jpeg"} and not head.startswith(b"\xff\xd8\xff"):
            raise ValidationError("محتوای فایل با پسوند تصویر مطابقت ندارد.")
        if suffix == ".png" and not head.startswith(b"\x89PNG\r\n\x1a\n"):
            raise ValidationError("محتوای فایل با پسوند تصویر مطابقت ندارد.")
        return
    if suffix == ".pdf" and head.startswith(b"%PDF-"):
        file_obj.seek(0, 2)
        file_obj.seek(max(0, file_obj.tell() - 2048))
        tail = file_obj.read()
        file_obj.seek(0)
        if b"%%EOF" not in tail:
            raise ValidationError("ساختار فایل PDF رسید کامل نیست.")
        return
    file_obj.seek(0)
    raise ValidationError("محتوای فایل با فرمت مجاز رسید مطابقت ندارد.")



class PaymentSettings(models.Model):
    """Singleton-like admin-managed bank transfer configuration; never expose via public serializers."""
    card_number = models.CharField(max_length=32, blank=True)
    account_holder = models.CharField(max_length=120, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.pk = 1
        # A fixed primary key turns subsequent create() calls into updates.
        kwargs.pop("force_insert", None)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("تنظیمات پرداخت قابل حذف نیست.")

    def __str__(self):
        return "تنظیمات کارت‌به‌کارت"


class PaymentOrder(models.Model):
    class ProductType(models.TextChoices):
        SUBSCRIPTION = "subscription", "اشتراک"
        EXAM = "exam", "خرید آزمون"

    class PaymentProvider(models.TextChoices):
        MANUAL = "manual", "پرداخت دستی"
        CAFEBAZAAR = "cafebazaar", "کافه‌بازار"

    class Status(models.TextChoices):
        AWAITING_PAYMENT = "awaiting_payment", "در انتظار پرداخت"
        UNDER_REVIEW = "under_review", "در انتظار بررسی"
        APPROVED = "approved", "تأییدشده"
        REJECTED = "rejected", "ردشده"
        CANCELLED = "cancelled", "لغوشده"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="payment_orders")
    product_type = models.CharField(max_length=16, choices=ProductType.choices)
    payment_provider = models.CharField(
        max_length=16, choices=PaymentProvider.choices, default=PaymentProvider.MANUAL
    )
    plan = models.ForeignKey("subscriptions.SubscriptionPlan", null=True, blank=True, on_delete=models.PROTECT)
    exam = models.ForeignKey("exams.Exam", null=True, blank=True, on_delete=models.PROTECT)
    amount_irr = models.PositiveBigIntegerField()
    plan_duration_days_snapshot = models.PositiveSmallIntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AWAITING_PAYMENT)
    tracking_code = models.CharField(max_length=100, blank=True)
    receipt = models.FileField(
        upload_to=receipt_upload_path,
        validators=[FileExtensionValidator(["jpg", "jpeg", "png", "pdf"]), validate_receipt_size, validate_receipt_content],
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
        indexes = [models.Index(fields=["user", "status"], name="pay_user_status_idx")]

    def clean(self):
        if self.amount_irr < 1:
            raise ValidationError({"amount_irr": "مبلغ سفارش باید بیشتر از صفر باشد."})
        if self.product_type == self.ProductType.SUBSCRIPTION and (not self.plan_id or self.exam_id):
            raise ValidationError("سفارش اشتراک باید فقط یک طرح اشتراک داشته باشد.")
        if self.product_type == self.ProductType.SUBSCRIPTION and self.plan_duration_days_snapshot is not None and self.plan_duration_days_snapshot < 1:
            raise ValidationError("مدت ثبت‌شده اشتراک باید بیشتر از صفر باشد.")
        if self.product_type == self.ProductType.EXAM and (not self.exam_id or self.plan_id):
            raise ValidationError("سفارش آزمون باید فقط یک آزمون داشته باشد.")

    def save(self, *args, **kwargs):
        if self.pk and PaymentOrder.objects.filter(pk=self.pk).exists():
            old = PaymentOrder.objects.get(pk=self.pk)
            immutable = ("user_id", "product_type", "payment_provider", "plan_id", "exam_id", "amount_irr", "plan_duration_days_snapshot")
            if any(getattr(old, field) != getattr(self, field) for field in immutable):
                raise ValidationError("مشخصات و مبلغ سفارش پس از ایجاد قابل تغییر نیست.")
            if old.status == self.Status.APPROVED:
                if self.status != old.status or self.receipt != old.receipt:
                    raise ValidationError("سفارش تأییدشده قابل تغییر نیست.")
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.id} · {self.amount_irr:,} ریال"


class PurchasedExamAccess(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="purchased_exam_access")
    exam = models.ForeignKey("exams.Exam", on_delete=models.PROTECT)
    source_order = models.OneToOneField(PaymentOrder, on_delete=models.PROTECT, related_name="granted_exam_access")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "exam"], name="uq_user_purchased_exam"),
        ]

    def __str__(self):
        return f"{self.user} · {self.exam}"



class BazaarSubscriptionPurchase(models.Model):
    """Server-verified Bazaar purchase metadata; raw purchase tokens are never stored."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField(
        PaymentOrder,
        on_delete=models.PROTECT,
        related_name="bazaar_purchase",
    )
    product_id = models.CharField(max_length=100)
    purchase_token_hash = models.CharField(max_length=64, unique=True)
    linked_subscription_token_hash = models.CharField(max_length=64, blank=True)
    purchased_at = models.DateTimeField()
    valid_until = models.DateTimeField()
    auto_renewing = models.BooleanField(default=False)
    verified_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-verified_at"]
        indexes = [
            models.Index(fields=["product_id", "valid_until"], name="bazaar_sku_valid_idx"),
        ]

    def clean(self):
        if self.valid_until <= self.purchased_at:
            raise ValidationError("تاریخ اعتبار خرید بازار معتبر نیست.")

    def __str__(self):
        return f"{self.product_id} · {self.order_id}"
