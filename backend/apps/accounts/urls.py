from django.urls import path

from .views import ProfileView, RequestOTPView, VerifyOTPView

urlpatterns = [
    path("profile/", ProfileView.as_view(), name="profile"),
    path("auth/request-otp/", RequestOTPView.as_view(), name="request-otp"),
    path("auth/verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),
]
