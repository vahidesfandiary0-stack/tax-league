from django.db import migrations, models


def seed_default_slides(apps, schema_editor):
    ShowcaseSlide = apps.get_model("notifications", "ShowcaseSlide")
    db = schema_editor.connection.alias
    ShowcaseSlide.objects.using(db).all().update(sort_order=models.F("sort_order") + 2)
    ShowcaseSlide.objects.using(db).get_or_create(
        kind="founder",
        title="بنیانگذار لیگ : وحید اسفندیاری نژاد",
        defaults={
            "body": "بنیانگذار لیگ : وحید اسفندیاری نژاد",
            "sort_order": 0,
            "duration_seconds": 5,
            "is_active": True,
        },
    )
    ShowcaseSlide.objects.using(db).get_or_create(
        kind="logo",
        title="لیگ نخبگان مالیاتی",
        defaults={
            "body": "رقابت کن، رتبه بگیر، نخبه شو!",
            "sort_order": 1,
            "duration_seconds": 5,
            "is_active": True,
        },
    )


class Migration(migrations.Migration):
    dependencies = [("notifications", "0002_showcaseslide")]

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
                ],
                max_length=20,
            ),
        ),
        migrations.RunPython(seed_default_slides, migrations.RunPython.noop),
    ]
