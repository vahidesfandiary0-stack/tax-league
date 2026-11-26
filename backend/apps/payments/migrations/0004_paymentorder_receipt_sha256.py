from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("payments", "0003_purchasedexamaccess"),
    ]

    operations = [
        migrations.AddField(
            model_name="paymentorder",
            name="receipt_sha256",
            field=models.CharField(blank=True, default="", max_length=64),
        ),
        migrations.AddConstraint(
            model_name="paymentorder",
            constraint=models.UniqueConstraint(
                condition=~models.Q(receipt_sha256=""),
                fields=("receipt_sha256",),
                name="uq_payment_receipt_sha256",
            ),
        ),
    ]
