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
        migrations.AddConstraint(
            model_name="leagueseason",
            constraint=models.UniqueConstraint(
                fields=("status",),
                condition=models.Q(status="active"),
                name="uq_single_active_league_season",
            ),
        ),
        migrations.CreateModel(
            name="LeagueSeasonEvent",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("kind", models.CharField(choices=[("activated", "فعال‌سازی فصل"), ("closed", "بستن فصل")], max_length=16)),
                ("note", models.CharField(blank=True, max_length=500)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("actor", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="league_season_events", to=settings.AUTH_USER_MODEL)),
                ("season", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="events", to="league.leagueseason")),
            ],
            options={"ordering": ["created_at", "id"]},
        ),
    ]
