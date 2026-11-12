import uuid
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("questions", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Exam",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=200)),
                ("kind", models.CharField(choices=[("daily", "آزمون روزانه"), ("weekly", "آزمون هفتگی"), ("mock", "آزمون جامع")], max_length=16)),
                ("description", models.TextField(blank=True)),
                ("duration_minutes", models.PositiveSmallIntegerField(default=30)),
                ("max_attempts", models.PositiveSmallIntegerField(default=1)),
                ("starts_at", models.DateTimeField(blank=True, null=True)),
                ("ends_at", models.DateTimeField(blank=True, null=True)),
                ("status", models.CharField(choices=[("draft", "پیش‌نویس"), ("published", "منتشرشده"), ("archived", "بایگانی")], default="draft", max_length=12)),
                ("counts_for_league", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="ExamAttempt",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("status", models.CharField(choices=[("in_progress", "در حال برگزاری"), ("submitted", "تحویل‌شده"), ("expired", "مهلت‌تمام‌شده")], default="in_progress", max_length=16)),
                ("started_at", models.DateTimeField()),
                ("deadline_at", models.DateTimeField()),
                ("submitted_at", models.DateTimeField(blank=True, null=True)),
                ("score", models.IntegerField(blank=True, null=True)),
                ("correct_count", models.PositiveSmallIntegerField(default=0)),
                ("wrong_count", models.PositiveSmallIntegerField(default=0)),
                ("blank_count", models.PositiveSmallIntegerField(default=0)),
                ("exam", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="attempts", to="exams.exam")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="exam_attempts", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-started_at"]},
        ),
        migrations.CreateModel(
            name="ExamQuestion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("position", models.PositiveSmallIntegerField()),
                ("points_correct", models.SmallIntegerField(default=10)),
                ("points_wrong", models.SmallIntegerField(default=-3)),
                ("exam", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="exam_questions", to="exams.exam")),
                ("question", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="questions.question")),
            ],
            options={"ordering": ["position"]},
        ),
        migrations.CreateModel(
            name="AttemptQuestion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("source_question_id", models.UUIDField()),
                ("position", models.PositiveSmallIntegerField()),
                ("prompt", models.TextField()),
                ("explanation", models.TextField(blank=True)),
                ("subject", models.CharField(max_length=32)),
                ("points_correct", models.SmallIntegerField(default=10)),
                ("points_wrong", models.SmallIntegerField(default=-3)),
                ("attempt", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="questions", to="exams.examattempt")),
            ],
            options={"ordering": ["position"]},
        ),
        migrations.CreateModel(
            name="AttemptOption",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("source_option_id", models.BigIntegerField()),
                ("position", models.PositiveSmallIntegerField()),
                ("text", models.TextField()),
                ("is_correct", models.BooleanField(default=False)),
                ("attempt_question", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="options", to="exams.attemptquestion")),
            ],
            options={"ordering": ["position"]},
        ),
        migrations.CreateModel(
            name="AttemptAnswer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("answered_at", models.DateTimeField(auto_now=True)),
                ("attempt_question", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="answer", to="exams.attemptquestion")),
                ("selected_option", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to="exams.attemptoption")),
            ],
        ),
        migrations.AddConstraint(model_name="examquestion", constraint=models.UniqueConstraint(fields=("exam", "position"), name="uq_exam_question_position")),
        migrations.AddConstraint(model_name="examquestion", constraint=models.UniqueConstraint(fields=("exam", "question"), name="uq_exam_question")),
        migrations.AddIndex(model_name="examattempt", index=models.Index(fields=["user", "exam", "status"], name="exams_user_exam_status_idx")),
        migrations.AddConstraint(model_name="attemptquestion", constraint=models.UniqueConstraint(fields=("attempt", "position"), name="uq_attempt_question_position")),
        migrations.AddConstraint(model_name="attemptoption", constraint=models.UniqueConstraint(fields=("attempt_question", "position"), name="uq_attempt_option_position")),
    ]
