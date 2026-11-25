import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("subscriptions", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="AcademyContent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("slug", models.SlugField(max_length=160, unique=True)),
                ("title", models.CharField(max_length=200)),
                ("summary", models.CharField(max_length=500)),
                ("category", models.CharField(choices=[
                    ("foundations", "مبانی تخصصی"),
                    ("trapology", "تله‌شناسی"),
                    ("case_study", "تحلیل پرونده"),
                    ("checklist", "چک‌لیست و مرور"),
                ], max_length=24)),
                ("body", models.TextField()),
                ("source_title", models.CharField(max_length=300)),
                ("source_url", models.URLField(max_length=1500)),
                ("legal_effective_date", models.DateField(blank=True, null=True)),
                ("is_exclusive", models.BooleanField(default=True)),
                ("is_active", models.BooleanField(default=False)),
                ("sort_order", models.PositiveSmallIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "محتوای آکادمی",
                "verbose_name_plural": "محتواهای آکادمی",
                "ordering": ["sort_order", "-updated_at", "pk"],
            },
        ),
    ]
