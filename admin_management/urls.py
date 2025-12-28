from django.urls import path
from admin_management.views import *

urlpatterns = [
    path('create-staff', CreateStaffAPIView.as_view(), name="create_staff"),


    path('list-staff', ListStaffAPIView.as_view(), name="list_staff"),
    path('delete-staff/<int:pk>', DeleteStaffAPIView.as_view(), name="delete_staff"),
    path("enable-login/<int:pk>", EnableLoginForStaffAPIView.as_view(), name="enable-staff-login"),
    path("disable-login/<int:pk>", DisableLoginForStaffAPIView.as_view(), name="disable-staff-login"),




     #dashboard URLs
    path('dashboard-metrics', DashboardSummaryAPIView.as_view(), name="dashboard-metrics"),
    path('monthly-trend', MonthlyTrendAPIView.as_view(), name="monthly-trend"),
    path('booking-progress', BookingProgressAPIView.as_view(), name="booking-progress"),
    path('monthly-trend-line',MonthlyTrendLineAPIView.as_view(), name="monthly-trend-line"),

    path('request-otp',RequestOTPAPIView.as_view(), name="request_otp"),
    path('verify-otp',VerifyOTPAPIView.as_view(), name="verify_otp"),

]
