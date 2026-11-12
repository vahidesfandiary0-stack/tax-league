from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.exams.models import ExamAttempt
from apps.exams.services import finalize_attempt


class Command(BaseCommand):
    help = "Finalize exam attempts whose server-side deadline has passed."

    def handle(self, *args, **options):
        now = timezone.now()
        attempt_ids = list(
            ExamAttempt.objects.filter(
                status=ExamAttempt.Status.IN_PROGRESS,
                deadline_at__lte=now,
            ).order_by("deadline_at").values_list("id", flat=True)[:500]
        )
        finalized = 0
        for attempt_id in attempt_ids:
            attempt = ExamAttempt.objects.select_related("user", "exam").get(pk=attempt_id)
            finalize_attempt(attempt.pk, attempt.user)
            finalized += 1
        self.stdout.write(self.style.SUCCESS(f"Finalized {finalized} expired attempt(s)."))
