from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


ROLE_PERMISSIONS = {
    "محتوا و بانک سؤال": {
        "questions": {
            "question": ("view", "add", "change"),
            "questionoption": ("view", "add", "change", "delete"),
        },
    },
    "مدیر آزمون": {
        "exams": {
            "exam": ("view", "add", "change"),
            "examquestion": ("view", "add", "change", "delete"),
        },
        "questions": {
            "question": ("view",),
            "questionoption": ("view",),
        },
    },
    "مسئول پرداخت": {
        "payments": {
            "paymentorder": ("view", "change"),
        },
        "subscriptions": {
            "subscriptionplan": ("view",),
            "usersubscription": ("view",),
        },
    },
    "پشتیبان": {
        "support": {
            "supportticket": ("view", "change"),
            "supportmessage": ("view",),
        },
    },
    "مدیر لیگ": {
        "league": {
            "leagueseason": ("view", "add", "change"),
            "leaguescoreentry": ("view",),
        },
    },
}


def sync_staff_roles():
    """Create/update least-privilege groups. Superusers remain the only role administrators."""
    for group_name, apps in ROLE_PERMISSIONS.items():
        group, _ = Group.objects.get_or_create(name=group_name)
        permissions = []
        for app_label, models in apps.items():
            for model_name, actions in models.items():
                content_type = ContentType.objects.get(app_label=app_label, model=model_name)
                for action in actions:
                    codename = f"{action}_{model_name}"
                    permissions.append(Permission.objects.get(content_type=content_type, codename=codename))
        group.permissions.set(permissions)
