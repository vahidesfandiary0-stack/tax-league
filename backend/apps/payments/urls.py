from django.urls import path

from .views import (
    AdminReceiptDownloadView, CreatePaymentOrderView, MySubscriptionView, PaymentInstructionsView, PaymentOrderDetailView,
    PaymentOrderListView, SubmitPaymentView, SubscriptionPlanListView,
)

urlpatterns = [
    path("plans/", SubscriptionPlanListView.as_view(), name="subscription-plans"),
    path("subscription/me/", MySubscriptionView.as_view(), name="my-subscription"),
    path("instructions/", PaymentInstructionsView.as_view(), name="payment-instructions"),
    path("orders/", PaymentOrderListView.as_view(), name="payment-order-list"),
    path("orders/create/", CreatePaymentOrderView.as_view(), name="payment-order-create"),
    path("orders/<uuid:order_id>/", PaymentOrderDetailView.as_view(), name="payment-order-detail"),
    path("orders/<uuid:order_id>/submit/", SubmitPaymentView.as_view(), name="payment-submit"),
    path("staff/orders/<uuid:order_id>/receipt/", AdminReceiptDownloadView.as_view(), name="payment-admin-receipt"),
]
