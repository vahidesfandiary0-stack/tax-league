from django.urls import path

from .views import AcademyContentDetailView, AcademyContentListView

urlpatterns = [
    path("content/", AcademyContentListView.as_view(), name="academy-content-list"),
    path("content/<slug:slug>/", AcademyContentDetailView.as_view(), name="academy-content-detail"),
]
