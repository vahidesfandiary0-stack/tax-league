import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("payments", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="SubscriptionPlan",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=100)),
                ("period", models.CharField(choices=[("monthly", "ماهانه"), ("quarterly", "سه‌ماهه"), ("annual", "سالانه")], max_length=12, unique=True)),
                ("duration_days", models.PositiveSmallIntegerField()),
                ("price_irr", models.PositiveBigIntegerField()),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["duration_days"]},
        ),
        migrations.CreateModel(
            name="UserSubscription",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("starts_at", models.DateTimeField()),
                ("ends_at", models.DateTimeField()),
                ("status", models.CharField(choices=[("active", "فعال"), ("expired", "منقضی"), ("revoked", "لغوشده")], default="active", max_length=10)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("plan", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="subscriptions.subscriptionplan")),
                ("source_order", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="granted_subscription", to="payments.paymentorder")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="subscriptions", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-ends_at"]},
        ),
        migrations.AddIndex(
            model_name="usersubscription",
            index=models.Index(fields=["user", "status", "ends_at"], name="subs_user_status_end_idx"),
        ),
    ]
