from django.contrib.admin.views.decorators import user_passes_test
from django.shortcuts import render
from django.utils import timezone

from apps.accounts.models import User
from apps.exams.models import Exam
from apps.league.models import LeagueAppeal, LeagueSeason
from apps.payments.models import PaymentOrder
from apps.questions.models import Question
from apps.subscriptions.models import UserSubscription


@user_passes_test(lambda user: user.is_active and user.is_superuser, login_url="admin:login")
def dashboard(request):
    now = timezone.now()
    context = {
        "user_count": User.objects.count(),
        "pending_payment_count": PaymentOrder.objects.filter(
            status=PaymentOrder.Status.UNDER_REVIEW
        ).count(),
        "pending_question_count": Question.objects.filter(
            status=Question.Status.PENDING
        ).count(),
        "published_exam_count": Exam.objects.filter(
            status=Exam.Status.PUBLISHED
        ).count(),
        "active_subscription_count": UserSubscription.objects.filter(
            status=UserSubscription.Status.ACTIVE,
            starts_at__lte=now,
            ends_at__gt=now,
        ).count(),
        "pending_appeal_count": LeagueAppeal.objects.filter(status=LeagueAppeal.Status.PENDING).count(),
        "active_season_count": LeagueSeason.objects.filter(
            status=LeagueSeason.Status.ACTIVE
        ).count(),
        "recent_payments": PaymentOrder.objects.select_related("user").order_by(
            "-created_at"
        )[:8],
    }
    return render(request, "admin/dashboard.html", context)
