import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("questions", "0002_question_variant_config"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="QuestionPremiumLesson",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("traps_and_techniques", models.TextField(blank=True)),
                ("trap_detection_signals", models.TextField(blank=True)),
                ("distractor_analysis", models.TextField(blank=True)),
                ("fast_solving_method", models.TextField(blank=True)),
                ("setter_insight", models.TextField(blank=True)),
                ("common_mistakes", models.TextField(blank=True)),
                ("supplementary_practice", models.TextField(blank=True)),
                ("practice_answer", models.TextField(blank=True)),
                ("legal_source_reference", models.CharField(blank=True, max_length=500)),
                ("legal_effective_date", models.DateField(blank=True, null=True)),
                ("status", models.CharField(choices=[("draft", "پیش‌نویس"), ("review", "در انتظار بازبینی"), ("approved", "تأییدشده"), ("published", "منتشرشده")], default="draft", max_length=12)),
                ("reviewed_at", models.DateTimeField(blank=True, null=True)),
                ("published_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("author", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="authored_premium_lessons", to=settings.AUTH_USER_MODEL)),
                ("question", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="premium_lesson", to="questions.question")),
                ("reviewer", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="reviewed_premium_lessons", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-updated_at"]},
        ),
        migrations.AddIndex(
            model_name="questionpremiumlesson",
            index=models.Index(fields=["status"], name="premium_lesson_status_idx"),
        ),
    ]
