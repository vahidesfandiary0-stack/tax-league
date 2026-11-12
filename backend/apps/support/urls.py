from django.urls import path

from .views import (
    SupportMessageCreateView, SupportTicketDetailView,
    SupportTicketListCreateView, SupportTicketStatusView,
)

urlpatterns = [
    path("tickets/", SupportTicketListCreateView.as_view(), name="support-ticket-list-create"),
    path("tickets/<uuid:ticket_id>/", SupportTicketDetailView.as_view(), name="support-ticket-detail"),
    path("tickets/<uuid:ticket_id>/messages/", SupportMessageCreateView.as_view(), name="support-ticket-message"),
    path("tickets/<uuid:ticket_id>/status/", SupportTicketStatusView.as_view(), name="support-ticket-status"),
]
