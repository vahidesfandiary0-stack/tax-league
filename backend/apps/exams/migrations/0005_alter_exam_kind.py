from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("exams", "0004_attempt_integrity_constraints"),
    ]

    operations = [
        migrations.AlterField(
            model_name="exam",
            name="kind",
            field=models.CharField(
                choices=[
                    ("nightly", "آزمون شبانه"),
                    ("daily", "آزمون روزانه"),
                    ("weekly", "آزمون هفتگی"),
                    ("mock", "آزمون جامع"),
                ],
                max_length=16,
            ),
        ),
    ]
