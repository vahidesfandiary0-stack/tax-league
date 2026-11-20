from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("questions", "0002_question_variant_config"),
    ]

    operations = [
        migrations.AlterField(
            model_name="question",
            name="difficulty",
            field=models.CharField(
                choices=[
                    ("easy", "آسان"),
                    ("medium", "متوسط"),
                    ("hard", "سخت"),
                    ("very_hard", "خیلی سخت"),
                    ("specialized", "تخصصی"),
                ],
                default="medium",
                max_length=12,
            ),
        ),
    ]
