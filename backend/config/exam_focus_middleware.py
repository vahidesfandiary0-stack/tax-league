from django.http import JsonResponse

from apps.exams.focus import get_exam_focus_state


RESTRICTED_API_PREFIXES = (
    "/api/v1/questions/",
    "/api/v1/payments/",
    "/api/v1/notifications/",
    "/api/v1/support/",
    "/api/v1/league/",
)


class ExamFocusModeMiddleware:
    """Temporarily reduce non-exam API work while a scheduled exam is running.

    Staff users keep full access. Exam delivery, answer saving, finalization,
    authentication, health checks, and the Django admin are never restricted.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        is_restricted_api = path.startswith(RESTRICTED_API_PREFIXES)
        user = getattr(request, "user", None)
        is_staff = bool(user and getattr(user, "is_authenticated", False) and getattr(user, "is_staff", False))

        if is_restricted_api and not is_staff and user and getattr(user, "is_authenticated", False):
            focus = get_exam_focus_state()
            if focus["active"]:
                response = JsonResponse(
                    {
                        "code": "EXAM_FOCUS_MODE",
                        "detail": "در زمان برگزاری آزمون، این بخش موقتاً غیرفعال است.",
                        "resume_at": focus["ends_at"],
                    },
                    status=423,
                )
                response["Cache-Control"] = "no-store"
                return response

        return self.get_response(request)
