from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("payments", "0005_paymentorder_payment_provider"),
    ]

    operations = [
        migrations.AddField(
            model_name="paymentorder",
            name="plan_duration_days_snapshot",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
    ]
