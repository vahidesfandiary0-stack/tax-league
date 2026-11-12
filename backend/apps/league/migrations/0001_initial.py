import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("exams", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="LeagueSeason",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=160)),
                ("starts_at", models.DateTimeField()),
                ("ends_at", models.DateTimeField()),
                ("status", models.CharField(choices=[("draft", "پیش‌نویس"), ("active", "فعال"), ("closed", "پایان‌یافته")], default="draft", max_length=12)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-starts_at"]},
        ),
        migrations.AddConstraint(
            model_name="leagueseason",
            constraint=models.CheckConstraint(condition=models.Q(("ends_at__gt", models.F("starts_at"))), name="league_season_dates_valid"),
        ),
        migrations.CreateModel(
            name="LeagueScoreEntry",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("score", models.IntegerField()),
                ("correct_count", models.PositiveSmallIntegerField()),
                ("wrong_count", models.PositiveSmallIntegerField()),
                ("elapsed_seconds", models.PositiveIntegerField()),
                ("recorded_at", models.DateTimeField(auto_now_add=True)),
                ("attempt", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="league_entry", to="exams.examattempt")),
                ("season", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="score_entries", to="league.leagueseason")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="league_score_entries", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-score", "-correct_count", "wrong_count", "elapsed_seconds"]},
        ),
        migrations.AddIndex(
            model_name="leaguescoreentry",
            index=models.Index(fields=["season", "user"], name="league_lea_season_6d9f1a_idx"),
        ),
        migrations.AddIndex(
            model_name="leaguescoreentry",
            index=models.Index(fields=["season", "-score"], name="league_lea_season_23b6b1_idx"),
        ),
    ]
