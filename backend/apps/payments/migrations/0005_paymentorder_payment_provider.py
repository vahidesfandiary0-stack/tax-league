from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0004_bazaarsubscriptionpurchase'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentorder',
            name='payment_provider',
            field=models.CharField(choices=[('manual', 'پرداخت دستی'), ('cafebazaar', 'کافه\u200cبازار')], default='manual', max_length=16),
        ),
    ]
