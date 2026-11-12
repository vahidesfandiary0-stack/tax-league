from django.urls import include, path
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

class HealthView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"status": "ok", "service": "tax-league-api"})

urlpatterns = [
    path("health/", HealthView.as_view(), name="health"),
    path("questions/", include("apps.questions.urls")),
    path("exams/", include("apps.exams.urls")),
    path("league/", include("apps.league.urls")),
]
