from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("questions", "0003_designer_revisions"),
        ("exams", "0005_exam_night_kind"),
    ]

    operations = [
        migrations.AddField(
            model_name="question",
            name="premium_analysis",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="attemptquestion",
            name="premium_analysis",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
