import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("league", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="LeagueScoreAdjustment",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("score_delta", models.IntegerField()),
                ("reason", models.CharField(max_length=500)),
                ("idempotency_key", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("actor", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="league_score_adjustments", to=settings.AUTH_USER_MODEL)),
                ("entry", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="adjustments", to="league.leaguescoreentry")),
            ],
            options={"ordering": ["created_at", "id"]},
        ),
        migrations.AddIndex(
            model_name="leaguescoreadjustment",
            index=models.Index(fields=["entry", "created_at"], name="league_adj_entry_time_idx"),
        ),
    ]
