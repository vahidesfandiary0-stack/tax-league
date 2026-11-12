import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.core.validators
import apps.payments.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("exams", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="PaymentSettings",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("card_number", models.CharField(blank=True, max_length=32)),
                ("account_holder", models.CharField(blank=True, max_length=120)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="PaymentOrder",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("product_type", models.CharField(choices=[("subscription", "اشتراک"), ("exam", "خرید آزمون")], max_length=16)),
                ("amount_irr", models.PositiveBigIntegerField()),
                ("status", models.CharField(choices=[("awaiting_payment", "در انتظار پرداخت"), ("under_review", "در انتظار بررسی"), ("approved", "تأییدشده"), ("rejected", "ردشده"), ("cancelled", "لغوشده")], default="awaiting_payment", max_length=20)),
                ("tracking_code", models.CharField(blank=True, max_length=100)),
                ("receipt", models.FileField(blank=True, upload_to=apps.payments.models.receipt_upload_path, validators=[django.core.validators.FileExtensionValidator(["jpg", "jpeg", "png", "pdf"]), apps.payments.models.validate_receipt_size])),
                ("user_note", models.CharField(blank=True, max_length=500)),
                ("review_note", models.CharField(blank=True, max_length=500)),
                ("reviewed_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("exam", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to="exams.exam")),
                ("reviewer", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="reviewed_payment_orders", to=settings.AUTH_USER_MODEL)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="payment_orders", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.AddIndex(
            model_name="paymentorder",
            index=models.Index(fields=["user", "status"], name="pay_user_status_idx"),
        ),
    ]
