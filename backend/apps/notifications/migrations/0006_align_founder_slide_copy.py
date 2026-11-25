from django.db import migrations


OLD_FOUNDER_TITLES = (
    "بنیانگذار لیگ : وحید اسفندیاری",
    "بنیانگذار لیگ : وحید اسفندیاری نژاد",
)
NEW_FOUNDER_TITLE = "بنیان‌گذار لیگ: وحید اسفندیاری"


def align_default_founder_copy(apps, schema_editor):
    ShowcaseSlide = apps.get_model("notifications", "ShowcaseSlide")
    slides = ShowcaseSlide.objects.using(schema_editor.connection.alias).filter(
        kind="founder",
        title__in=OLD_FOUNDER_TITLES,
    )
    slides.update(title=NEW_FOUNDER_TITLE)


class Migration(migrations.Migration):
    dependencies = [
        ("notifications", "0005_showcaseslide_image"),
    ]

    operations = [
        migrations.RunPython(align_default_founder_copy, migrations.RunPython.noop),
    ]
