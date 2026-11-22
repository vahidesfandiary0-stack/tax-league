# Generated for designer authoring versions and specialist difficulty levels.
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("questions", "0002_question_variant_config"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name="question",
            name="difficulty",
            field=models.CharField(
                choices=[
                    ("easy", "آسان"), ("medium", "متوسط"), ("hard", "سخت"),
                    ("very_hard", "خیلی سخت"), ("specialist", "تخصصی"),
                ],
                default="medium", max_length=12,
            ),
        ),
        migrations.CreateModel(
            name="QuestionRevision",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("version", models.PositiveIntegerField()),
                ("snapshot", models.JSONField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("changed_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="question_revisions", to=settings.AUTH_USER_MODEL)),
                ("question", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="revisions", to="questions.question")),
            ],
            options={"ordering": ["-version"]},
        ),
        migrations.AddConstraint(
            model_name="questionrevision",
            constraint=models.UniqueConstraint(fields=("question", "version"), name="uq_question_revision_version"),
        ),
    ]
