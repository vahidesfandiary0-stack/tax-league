import uuid
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("league", "0002_leaguescoreadjustment"),
        ("exams", "0002_exam_purchase_fields"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name="LeagueAppeal",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("reason", models.CharField(max_length=200)),
                ("details", models.TextField(max_length=4000)),
                ("status", models.CharField(choices=[("pending", "در انتظار بررسی"), ("approved", "پذیرفته‌شده"), ("rejected", "ردشده")], default="pending", max_length=12)),
                ("decision_note", models.CharField(blank=True, max_length=1000)),
                ("score_delta", models.IntegerField(blank=True, null=True)),
                ("reviewed_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("adjustment", models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="appeal", to="league.leaguescoreadjustment")),
                ("attempt", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="league_appeal", to="exams.examattempt")),
                ("reviewer", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="reviewed_league_appeals", to=settings.AUTH_USER_MODEL)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="league_appeals", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.AddIndex(model_name="leagueappeal", index=models.Index(fields=["status", "created_at"], name="league_appeal_status_idx")),
    ]
