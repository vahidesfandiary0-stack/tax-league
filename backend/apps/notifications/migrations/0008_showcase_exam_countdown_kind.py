from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("notifications", "0007_restore_founder_job_title"),
    ]

    operations = [
        migrations.AlterField(
            model_name="showcaseslide",
            name="kind",
            field=models.CharField(
                choices=[
                    ("founder", "بنیان‌گذار"),
                    ("logo", "لوگوی لیگ"),
                    ("message", "پیام مدیریتی"),
                    ("advertisement", "تبلیغات"),
                    ("exam_countdown", "شمارش معکوس آزمون رسمی"),
                ],
                max_length=20,
            ),
        ),
    ]
