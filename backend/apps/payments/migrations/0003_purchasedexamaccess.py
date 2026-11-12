import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("payments", "0002_paymentorder_plan"),
        ("exams", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="PurchasedExamAccess",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("exam", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="exams.exam")),
                ("source_order", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="granted_exam_access", to="payments.paymentorder")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="purchased_exam_access", to=settings.AUTH_USER_MODEL)),
            ],
            options={"constraints": [models.UniqueConstraint(fields=("user", "exam"), name="uq_user_purchased_exam")]},
        ),
    ]
