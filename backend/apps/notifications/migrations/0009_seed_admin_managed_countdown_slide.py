from django.db import migrations


def ensure_countdown_slide(apps, schema_editor):
    ShowcaseSlide = apps.get_model("notifications", "ShowcaseSlide")
    ShowcaseSlide.objects.using(schema_editor.connection.alias).update_or_create(
        kind="exam_countdown",
        defaults={
            "title": "آزمون بعدی",
            "body": "",
            "image_url": "",
            "sort_order": 2,
            "duration_seconds": 8,
            "is_active": True,
        },
    )


class Migration(migrations.Migration):
    dependencies = [
        ("notifications", "0008_showcase_exam_countdown_kind"),
    ]

    operations = [
        migrations.RunPython(ensure_countdown_slide, migrations.RunPython.noop),
    ]
