import django.db.models.deletion
import django.utils.timezone
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Question",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("subject", models.CharField(choices=[("direct_tax", "مالیات‌های مستقیم"), ("vat", "مالیات بر ارزش افزوده"), ("taxpayer_system", "سامانه مؤدیان و پایانه‌های فروشگاهی"), ("disputes", "دادرسی مالیاتی"), ("audit", "حسابرسی مالیاتی"), ("other_laws", "قوانین و مقررات مرتبط")], max_length=32)),
                ("difficulty", models.CharField(choices=[("easy", "آسان"), ("medium", "متوسط"), ("hard", "سخت")], default="medium", max_length=12)),
                ("prompt", models.TextField()),
                ("explanation", models.TextField(blank=True)),
                ("source_reference", models.CharField(blank=True, max_length=500)),
                ("valid_from", models.DateField(blank=True, null=True)),
                ("valid_until", models.DateField(blank=True, null=True)),
                ("provenance", models.CharField(choices=[("official", "متن رسمی آزمون"), ("reconstructed", "بازسازی‌شده از منبع"), ("authored", "تألیفی")], default="authored", max_length=20)),
                ("provenance_note", models.CharField(blank=True, max_length=500)),
                ("status", models.CharField(choices=[("draft", "پیش‌نویس"), ("pending_review", "در انتظار بررسی"), ("approved", "تأییدشده"), ("rejected", "ردشده"), ("published", "منتشرشده")], default="draft", max_length=20)),
                ("version", models.PositiveIntegerField(default=1)),
                ("review_decision", models.CharField(blank=True, max_length=20)),
                ("review_reason", models.TextField(blank=True)),
                ("reviewed_at", models.DateTimeField(blank=True, null=True)),
                ("published_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("author", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="authored_questions", to=settings.AUTH_USER_MODEL)),
                ("reviewer", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="reviewed_questions", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="QuestionOption",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("position", models.PositiveSmallIntegerField()),
                ("text", models.TextField()),
                ("is_correct", models.BooleanField(default=False)),
                ("question", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="options", to="questions.question")),
            ],
            options={"ordering": ["position"]},
        ),
        migrations.AddConstraint(model_name="question", constraint=models.UniqueConstraint(fields=("id", "version"), name="uq_question_id_version")),
        migrations.AddIndex(model_name="question", index=models.Index(fields=["status", "subject"], name="questions_status_subject_idx")),
        migrations.AddIndex(model_name="question", index=models.Index(fields=["provenance"], name="questions_provenance_idx")),
        migrations.AddConstraint(model_name="questionoption", constraint=models.UniqueConstraint(fields=("question", "position"), name="uq_question_option_position")),
        migrations.AddConstraint(model_name="questionoption", constraint=models.CheckConstraint(condition=models.Q(("position__gte", 1), ("position__lte", 4)), name="ck_question_option_position_1_4")),
    ]
