from django.db import migrations


FOUNDER_TITLE = "بنیان‌گذار لیگ: وحید اسفندیاری"
FOUNDER_BODY = "حسابرس ارشد اداره کل امورمالیاتی خوزستان"


def restore_founder_job_title(apps, schema_editor):
    ShowcaseSlide = apps.get_model("notifications", "ShowcaseSlide")
    manager = ShowcaseSlide.objects.using(schema_editor.connection.alias)
    manager.filter(
        kind="founder",
        title=FOUNDER_TITLE,
        body="",
    ).update(body=FOUNDER_BODY)


class Migration(migrations.Migration):
    dependencies = [
        ("notifications", "0006_align_founder_slide_copy"),
    ]

    operations = [
        migrations.RunPython(restore_founder_job_title, migrations.RunPython.noop),
    ]
