from .models import Notification


def create_notification(*, recipient, kind, title, body, data=None):
    return Notification.objects.create(
        recipient=recipient,
        kind=kind,
        title=title,
        body=body,
        data=data or {},
    )
