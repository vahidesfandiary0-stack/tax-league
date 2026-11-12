from django.contrib import admin
from django.urls import include, path

from config.admin_dashboard import dashboard
from config.league_admin import league_appeals

urlpatterns = [
    path("admin/overview/", dashboard, name="admin-dashboard"),
    path("admin/league/appeals/", league_appeals, name="league-appeals"),
    path("admin/", admin.site.urls),
    path("api/v1/", include("config.api_urls")),
]
