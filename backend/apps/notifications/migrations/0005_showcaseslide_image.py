import apps.notifications.models
from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):
    dependencies = [
        ("notifications", "0004_update_founder_credentials"),
    ]

    operations = [
        migrations.AddField(
            model_name="showcaseslide",
            name="image",
            field=models.ImageField(
                blank=True,
                upload_to="showcase/",
                validators=[
                    django.core.validators.FileExtensionValidator(["jpg", "jpeg", "png", "webp"]),
                    apps.notifications.models.validate_showcase_image_size,
                ],
            ),
        ),
    ]
