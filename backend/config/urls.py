from django.contrib import admin
from django.urls import include, path

from config.admin_dashboard import dashboard

urlpatterns = [
    path("admin/overview/", dashboard, name="admin-dashboard"),
    path("admin/", admin.site.urls),
    path("api/v1/", include("config.api_urls")),
]
