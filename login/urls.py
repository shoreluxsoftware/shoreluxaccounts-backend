from django.urls import path
from .views import UnifiedLoginAPIView

urlpatterns = [
    path("login", UnifiedLoginAPIView.as_view(), name="unified-login"),
]
