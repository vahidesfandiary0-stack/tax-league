import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("questions", "0003_question_premium_lesson"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(model_name="question", name="source_verified_at", field=models.DateTimeField(blank=True, null=True)),
        migrations.AddField(
            model_name="question", name="source_verified_by",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="source_verified_questions", to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name="question", name="difficulty",
            field=models.CharField(choices=[("easy", "آسان"), ("medium", "متوسط"), ("hard", "سخت"), ("very_hard", "بسیار سخت"), ("specialized", "تخصصی")], default="medium", max_length=12),
        ),
    ]
