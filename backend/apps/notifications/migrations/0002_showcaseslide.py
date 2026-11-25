from django.db import migrations, models
from django.core.validators import MaxValueValidator, MinValueValidator


def create_default_showcase_slides(apps, schema_editor):
    Slide = apps.get_model("notifications", "ShowcaseSlide")
    db_alias = schema_editor.connection.alias
    Slide.objects.using(db_alias).get_or_create(
        kind="logo",
        defaults={
            "title": "",
            "body": "",
            "sort_order": 2,
            "duration_seconds": 5,
            "is_active": True,
        },
    )


class Migration(migrations.Migration):
    dependencies = [
        ("notifications", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ShowcaseSlide",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("kind", models.CharField(choices=[("founder", "بنیان‌گذار"), ("logo", "لوگوی لیگ"), ("message", "پیام مدیریتی"), ("advertisement", "تبلیغات")], max_length=20)),
                ("title", models.CharField(blank=True, max_length=160)),
                ("body", models.TextField(max_length=1200)),
                ("image_url", models.URLField(blank=True, max_length=1000)),
                ("sort_order", models.PositiveSmallIntegerField(default=0)),
                ("duration_seconds", models.PositiveSmallIntegerField(default=5, validators=[MinValueValidator(3), MaxValueValidator(15)])),
                ("starts_at", models.DateTimeField(blank=True, null=True)),
                ("ends_at", models.DateTimeField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "اسلاید مدیریتی صفحه خانه",
                "verbose_name_plural": "اسلایدهای مدیریتی صفحه خانه",
                "ordering": ["sort_order", "pk"],
            },
        ),
        migrations.RunPython(create_default_showcase_slides, migrations.RunPython.noop),
    ]
