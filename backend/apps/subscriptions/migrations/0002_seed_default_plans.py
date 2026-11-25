from django.db import migrations


PLANS = [
    ("monthly", "اشتراک ماهانه", 30, 1_990_000),
    ("quarterly", "اشتراک سه‌ماهه", 90, 4_990_000),
    ("annual", "اشتراک سالانه", 365, 14_990_000),
]


def seed_subscription_plans(apps, schema_editor):
    Plan = apps.get_model("subscriptions", "SubscriptionPlan")
    db = schema_editor.connection.alias
    for period, title, days, price in PLANS:
        Plan.objects.using(db).update_or_create(
            period=period,
            defaults={
                "title": title,
                "duration_days": days,
                "price_irr": price,
                "is_active": True,
            },
        )


class Migration(migrations.Migration):
    dependencies = [("subscriptions", "0001_initial")]

    operations = [
        migrations.RunPython(seed_subscription_plans, migrations.RunPython.noop),
    ]
