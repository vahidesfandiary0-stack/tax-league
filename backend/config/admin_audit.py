from django.contrib.admin.models import CHANGE, LogEntry


def record_admin_action(actor, objects, message):
    """Write successful sensitive admin actions to Django's protected admin log."""
    items = list(objects)
    if not items:
        return 0
    grouped = {}
    for obj in items:
        grouped.setdefault(obj.__class__, []).append(obj.pk)
    count = 0
    for model, object_ids in grouped.items():
        queryset = model._default_manager.filter(pk__in=object_ids)
        LogEntry.objects.log_actions(
            user_id=actor.pk,
            queryset=queryset,
            action_flag=CHANGE,
            change_message=message,
            single_object=False,
        )
        count += len(object_ids)
    return count
