from django.db import migrations


OLD_TITLE = "بنیانگذار لیگ : وحید اسفندیاری"
NEW_TITLE = "بنیانگذار لیگ : وحید اسفندیاری نژاد"
NEW_BODY = "حسابرس ارشد اداره کل امورمالیاتی خوزستان"


def update_default_founder_slide(apps, schema_editor):
    ShowcaseSlide = apps.get_model("notifications", "ShowcaseSlide")
    db_alias = schema_editor.connection.alias
    ShowcaseSlide.objects.using(db_alias).filter(
        kind="founder",
        title=OLD_TITLE,
    ).update(title=NEW_TITLE, body=NEW_BODY)


class Migration(migrations.Migration):
    dependencies = [
        ("notifications", "0003_founder_first_showcase_slide"),
    ]

    operations = [
        migrations.RunPython(update_default_founder_slide, migrations.RunPython.noop),
    ]
