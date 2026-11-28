from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("questions", "0003_designer_revisions"),
    ]

    operations = [
        migrations.AddField(
            model_name="question",
            name="premium_analysis",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
