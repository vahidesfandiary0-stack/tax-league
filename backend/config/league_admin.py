from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.utils import timezone

from apps.league.models import LeagueAppeal
from apps.league.services import review_league_appeal


@staff_member_required
def league_appeals(request):
    can_review = request.user.is_superuser or request.user.has_perm("league.change_leagueappeal")
    if not can_review:
        messages.error(request, "شما مجوز بررسی اعتراض‌های لیگ را ندارید.")
        return redirect("admin:index")

    if request.method == "POST":
        appeal_id = request.POST.get("appeal_id")
        decision = request.POST.get("decision")
        note = request.POST.get("decision_note", "")
        raw_delta = request.POST.get("score_delta", "").strip()
        try:
            delta = int(raw_delta) if raw_delta else None
            appeal = review_league_appeal(
                appeal_id, request.user, decision, note, delta
            )
            messages.success(request, f"اعتراض با وضعیت «{appeal.get_status_display()}» ثبت شد.")
        except (ValidationError, LeagueAppeal.DoesNotExist, ValueError) as exc:
            messages.error(request, str(exc))
        return redirect("league-appeals")

    pending = LeagueAppeal.objects.filter(status=LeagueAppeal.Status.PENDING).select_related(
        "attempt", "user", "attempt__exam"
    ).order_by("created_at")[:100]
    recent = LeagueAppeal.objects.exclude(status=LeagueAppeal.Status.PENDING).select_related(
        "attempt", "user", "reviewer"
    ).order_by("-reviewed_at")[:30]
    return render(request, "admin/league_appeals.html", {
        "pending_appeals": pending,
        "recent_appeals": recent,
        "pending_count": LeagueAppeal.objects.filter(status=LeagueAppeal.Status.PENDING).count(),
        "now": timezone.now(),
    })
