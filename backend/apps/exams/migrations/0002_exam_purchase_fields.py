from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("exams", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="exam",
            name="requires_purchase",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="exam",
            name="price_irr",
            field=models.PositiveBigIntegerField(default=0),
        ),
    ]
