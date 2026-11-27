from django.db import migrations, models


def seed_admin_managed_slides(apps, schema_editor):
    Slide = apps.get_model("notifications", "ShowcaseSlide")
    manager = Slide.objects.using(schema_editor.connection.alias)

    manager.filter(
        kind="founder",
        title__in=[
            "بنیانگذار لیگ : وحید اسفندیاری",
            "بنیان‌گذار لیگ: وحید اسفندیاری",
        ],
        body__in=[
            "",
            "مالک و بنیان‌گذار لیگ نخبگان مالیاتی",
            "حسابرس ارشد اداره کل امورمالیاتی خوزستان",
        ],
    ).update(
        title="بنیانگذار لیگ نخبگان : وحید اسفندیاری نژاد",
        body="حسابرس ارشد اداره کل امور مالیاتی استان خوزستان",
    )

    manager.filter(kind="logo", title="").update(
        title="رقابت کن، رتبه بگیر، نخبه شو!"
    )

    manager.get_or_create(
        kind="exam_countdown",
        defaults={
            "title": "شمارش معکوس آزمون بعدی",
            "body": "",
            "sort_order": 2,
            "duration_seconds": 8,
            "is_active": True,
        },
    )


class Migration(migrations.Migration):
    dependencies = [
        ("notifications", "0007_restore_founder_job_title"),
        ("exams", "0004_attempt_integrity_constraints"),
    ]

    operations = [
        migrations.AlterField(
            model_name="showcaseslide",
            name="kind",
            field=models.CharField(
                max_length=20,
                choices=[
                    ("founder", "بنیان‌گذار"),
                    ("logo", "لوگوی لیگ"),
                    ("message", "پیام مدیریتی"),
                    ("advertisement", "تبلیغات"),
                    ("exam_countdown", "شمارش معکوس آزمون رسمی"),
                ],
            ),
        ),
        migrations.RunPython(seed_admin_managed_slides, migrations.RunPython.noop),
    ]
