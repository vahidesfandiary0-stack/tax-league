from django.urls import path

from .views import (
    CreatePaymentOrderView, PaymentInstructionsView, PaymentOrderDetailView,
    PaymentOrderListView, SubmitPaymentView, SubscriptionPlanListView,
)

urlpatterns = [
    path("plans/", SubscriptionPlanListView.as_view(), name="subscription-plans"),
    path("instructions/", PaymentInstructionsView.as_view(), name="payment-instructions"),
    path("orders/", PaymentOrderListView.as_view(), name="payment-order-list"),
    path("orders/create/", CreatePaymentOrderView.as_view(), name="payment-order-create"),
    path("orders/<uuid:order_id>/", PaymentOrderDetailView.as_view(), name="payment-order-detail"),
    path("orders/<uuid:order_id>/submit/", SubmitPaymentView.as_view(), name="payment-submit"),
]
