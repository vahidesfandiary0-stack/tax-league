from django.db.models import Sum
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.exams.models import Exam, ExamAttempt
from apps.subscriptions.models import UserSubscription
from .models import LeagueScoreEntry


def _entry_payload(entry):
    correction = entry.adjustments.aggregate(total=Sum("score_delta"))["total"] or 0
    attempt = entry.attempt
    return {
        "attempt_id": str(attempt.pk), "exam_title": attempt.exam.title,
        "submitted_at": attempt.submitted_at, "score": entry.score + correction,
        "correct_count": entry.correct_count, "wrong_count": entry.wrong_count,
        "elapsed_seconds": entry.elapsed_seconds,
    }


def _sort_key(item):
    return (-item["score"], -item["correct_count"], item["wrong_count"],
            item["elapsed_seconds"], item["user_id"])


class LatestNightLeaderboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        exam = Exam.objects.filter(
            kind=Exam.Kind.NIGHT,
            status__in=[Exam.Status.PUBLISHED, Exam.Status.ARCHIVED],
            starts_at__isnull=False,
            starts_at__lte=timezone.now(),
        ).order_by("-starts_at", "-created_at").first()
        if exam is None:
            return Response({"exam": None, "results": []})
        entries = LeagueScoreEntry.objects.filter(
            attempt__exam=exam,
            attempt__status__in=[ExamAttempt.Status.SUBMITTED, ExamAttempt.Status.EXPIRED],
            attempt__submitted_at__isnull=False, attempt__score__isnull=False,
        ).select_related("attempt__exam", "user").prefetch_related("adjustments")
        best_by_user = {}
        for entry in entries:
            row = _entry_payload(entry)
            row.update(user_id=entry.user_id, display_name=entry.user.display_name or "کاربر")
            previous = best_by_user.get(entry.user_id)
            if previous is None or _sort_key(row) < _sort_key(previous):
                best_by_user[entry.user_id] = row
        ordered = sorted(best_by_user.values(), key=_sort_key)
        results = [
            {key: value for key, value in row.items() if key != "user_id"} | {"rank": index}
            for index, row in enumerate(ordered, start=1)
        ]
        return Response({"exam": {"id": str(exam.pk), "title": exam.title,
                                  "submitted_at": exam.starts_at},
                         "results": results})


class MyTopNightRecordsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        entries = LeagueScoreEntry.objects.filter(
            user=request.user, attempt__exam__kind=Exam.Kind.NIGHT,
            attempt__status__in=[ExamAttempt.Status.SUBMITTED, ExamAttempt.Status.EXPIRED],
            attempt__submitted_at__isnull=False, attempt__score__isnull=False,
        ).select_related("attempt__exam").prefetch_related("adjustments")
        rows = [_entry_payload(entry) for entry in entries]
        rows.sort(key=lambda row: (-row["score"], -row["correct_count"], row["wrong_count"],
                                   row["elapsed_seconds"], row["submitted_at"] or timezone.now()))
        return Response({"records": rows[:5], "total_valid_records": len(rows)})


class MyDetailedPerformanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        now = timezone.now()
        active = UserSubscription.objects.filter(
            user=request.user, status=UserSubscription.Status.ACTIVE,
            starts_at__lte=now, ends_at__gt=now,
        ).exists()
        if not active:
            return Response({"detail": "برای مشاهده تحلیل تفصیلی، اشتراک فعال لازم است.",
                             "subscription_required": True}, status=403)
        entries = list(LeagueScoreEntry.objects.filter(
            user=request.user, attempt__exam__kind=Exam.Kind.NIGHT,
            attempt__status__in=[ExamAttempt.Status.SUBMITTED, ExamAttempt.Status.EXPIRED],
            attempt__submitted_at__isnull=False, attempt__score__isnull=False,
        ).select_related("attempt__exam").prefetch_related("adjustments").order_by("attempt__submitted_at"))
        if not entries:
            return Response({"subscription_required": False, "data_available": False,
                             "detail": "هنوز نتیجه معتبر آزمون شبانه برای تحلیل وجود ندارد."})
        rows = [_entry_payload(entry) for entry in entries]
        count = len(rows)
        return Response({
            "subscription_required": False, "data_available": True,
            "summary": {
                "night_exams_count": count, "total_score": sum(row["score"] for row in rows),
                "average_score": round(sum(row["score"] for row in rows) / count, 2),
                "correct_total": sum(row["correct_count"] for row in rows),
                "wrong_total": sum(row["wrong_count"] for row in rows),
                "average_elapsed_seconds": round(sum(row["elapsed_seconds"] for row in rows) / count, 2),
            },
            "trend": rows[-10:],
        })
