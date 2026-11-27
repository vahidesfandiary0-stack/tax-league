from django.contrib import admin
from django.urls import include, path

from apps.notifications.views import showcase_image
from config.admin_dashboard import dashboard
from config.league_admin import league_appeals

urlpatterns = [
    path("media/showcase/<path:path>", showcase_image, name="showcase-image"),
    path("admin/overview/", dashboard, name="admin-dashboard"),
    path("admin/league/appeals/", league_appeals, name="admin-league-appeals"),
    path("admin/", admin.site.urls),
    path("api/v1/", include("config.api_urls")),
]
