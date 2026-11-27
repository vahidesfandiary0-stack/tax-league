from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("exams", "0005_exam_night_kind"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="exam",
            name="test_user",
            field=models.ForeignKey(
                blank=True,
                help_text="اگر تعیین شود، آزمون فقط برای همین کاربر نمایش داده می‌شود.",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="private_test_exams",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
