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
                    ("daily", "آزمون روزانه"),
                    ("weekly", "آزمون هفتگی"),
                    ("mock", "آزمون جامع"),
                    ("night", "آزمون شبانه"),
                ],
                max_length=16,
            ),
        ),
    ]
