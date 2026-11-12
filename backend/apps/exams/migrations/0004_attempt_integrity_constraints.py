from django.db import migrations, models
from django.db.models import F


class Migration(migrations.Migration):
    dependencies = [
        ("exams", "0002_exam_purchase_fields"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="examattempt",
            constraint=models.UniqueConstraint(
                fields=("exam", "user"),
                condition=models.Q(status="in_progress"),
                name="uq_exam_user_active_attempt",
            ),
        ),
        migrations.AddConstraint(
            model_name="examattempt",
            constraint=models.CheckConstraint(
                condition=models.Q(deadline_at__gt=F("started_at")),
                name="ck_attempt_deadline_after_start",
            ),
        ),
    ]
