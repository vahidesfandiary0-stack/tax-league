from django.db import migrations


def ensure_founder_first(apps, schema_editor):
    Slide = apps.get_model("notifications", "ShowcaseSlide")
    db_alias = schema_editor.connection.alias
    Slide.objects.using(db_alias).update_or_create(
        kind="founder",
        defaults={
            "title": "بنیانگذار لیگ : وحید اسفندیاری",
            "body": "",
            "image_url": "",
            "sort_order": 0,
            "duration_seconds": 5,
            "is_active": True,
        },
    )
    Slide.objects.using(db_alias).filter(kind="logo").update(sort_order=1)


class Migration(migrations.Migration):
    dependencies = [
        ("notifications", "0002_showcaseslide"),
    ]

    operations = [
        migrations.RunPython(ensure_founder_first, migrations.RunPython.noop),
    ]
