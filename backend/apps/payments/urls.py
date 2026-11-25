from django.urls import path

from .bazaar_views import BazaarCreateOrderView, BazaarRestoreView, BazaarVerifyOrderView
from .views import (
    AdminReceiptDownloadView, CreatePaymentOrderView, MySubscriptionView, PaymentInstructionsView, PaymentOrderDetailView,
    PaymentOrderListView, SubmitPaymentView, SubscriptionPlanListView,
)

urlpatterns = [
    path("bazaar/orders/", BazaarCreateOrderView.as_view(), name="bazaar-order-create"),
    path("bazaar/orders/<uuid:order_id>/verify/", BazaarVerifyOrderView.as_view(), name="bazaar-order-verify"),
    path("bazaar/restore/", BazaarRestoreView.as_view(), name="bazaar-restore"),
    path("plans/", SubscriptionPlanListView.as_view(), name="subscription-plans"),
    path("subscription/me/", MySubscriptionView.as_view(), name="my-subscription"),
    path("instructions/", PaymentInstructionsView.as_view(), name="payment-instructions"),
    path("orders/", PaymentOrderListView.as_view(), name="payment-order-list"),
    path("orders/create/", CreatePaymentOrderView.as_view(), name="payment-order-create"),
    path("orders/<uuid:order_id>/", PaymentOrderDetailView.as_view(), name="payment-order-detail"),
    path("orders/<uuid:order_id>/submit/", SubmitPaymentView.as_view(), name="payment-submit"),
    path("staff/orders/<uuid:order_id>/receipt/", AdminReceiptDownloadView.as_view(), name="payment-admin-receipt"),
]
