import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("payments", "0003_purchasedexamaccess"),
        ("subscriptions", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="BazaarPurchase",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("product_id", models.CharField(max_length=100)),
                ("purchase_token_hash", models.CharField(max_length=64, unique=True)),
                ("bazaar_order_id", models.CharField(blank=True, max_length=160)),
                ("expires_at", models.DateTimeField()),
                ("auto_renewing", models.BooleanField(default=False)),
                ("verified_at", models.DateTimeField(auto_now=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("order", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="bazaar_purchase", to="payments.paymentorder")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="bazaar_purchases", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddIndex(
            model_name="bazaarpurchase",
            index=models.Index(fields=["user", "product_id"], name="bazaar_user_product_idx"),
        ),
    ]
