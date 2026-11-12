from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("payments", "0001_initial"),
        ("subscriptions", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="paymentorder",
            name="plan",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to="subscriptions.subscriptionplan"),
        ),
    ]
