from django.contrib.admin.models import CHANGE, LogEntry
from django.contrib.contenttypes.models import ContentType


def record_admin_action(actor, objects, message):
    """Write successful sensitive admin actions to Django's protected admin log."""
    items = list(objects)
    if not items:
        return 0
    # Group by model so each content type is recorded correctly.
    grouped = {}
    for obj in items:
        grouped.setdefault(obj.__class__, []).append(obj)
    count = 0
    for model, rows in grouped.items():
        LogEntry.objects.log_actions(
            user_id=actor.pk,
            queryset=rows,
            action_flag=CHANGE,
            change_message=message,
            single_object=False,
        )
        count += len(rows)
    return count
