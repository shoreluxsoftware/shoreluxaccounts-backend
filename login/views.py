from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from admin_management.models import User

from admin_management.models import *
from admin_management.serializers import *
from datetime import datetime
# from login.sms_service import sms_service



from .email_service import EmailNotificationService


from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class UnifiedLoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        login_type = request.data.get("login_type")   # ADMIN or STAFF
        username = request.data.get("username")
        password = request.data.get("password")
        staff_id = request.data.get("staff_unique_id")

        # ---------------------------------------------------
        # Validate required fields
        # ---------------------------------------------------
        if not login_type:
            return Response(
                {"error": "login_type is required (ADMIN or STAFF)"},
                status=400
            )

        if not username or not password:
            return Response(
                {"error": "username and password are required"},
                status=400
            )

        # ---------------------------------------------------
        # Authenticate credentials
        # ---------------------------------------------------
        user = authenticate(username=username, password=password)
        if not user:
            return Response(
                {"error": "Invalid username or password"},
                status=401
            )

        # ===================================================
        # STAFF LOGIN
        # ===================================================
        if login_type == "STAFF":

            if user.role != "STAFF":
                return Response(
                    {"error": "This user is not a staff"},
                    status=403
                )

            if not user.can_login:
                return Response(
                    {"error": "Login access not enabled for this staff"},
                    status=403
                )

            if not staff_id:
                return Response(
                    {"error": "staff_unique_id is required for STAFF login"},
                    status=400
                )

            if user.staff_unique_id != staff_id:
                return Response(
                    {"error": "Invalid staff ID"},
                    status=401
                )

            # Send login SMS
            login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # sms_service.send_login_notification(
            #     username=user.username,
            #     staff_code=user.staff_unique_id,
            #     login_datetime=login_time
            # )

            email_service = EmailNotificationService()
            email_service.send_login_alert(
                username=user.username,
                staff_code=user.staff_unique_id,
                login_datetime=login_time
            )


            refresh = RefreshToken.for_user(user)

            return Response({
                "message": "Staff login successful",
                "role": "STAFF",
                "staff_unique_id": user.staff_unique_id,
                "token": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }
            }, status=200)

        # ===================================================
        # ADMIN LOGIN
        # ===================================================
        elif login_type == "ADMIN":

            if user.role != "ADMIN":
                return Response(
                    {"error": "This user is not an admin"},
                    status=403
                )

            # Admins do NOT need can_login
            login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # sms_service.send_login_notification(
            #     username=user.username,
            #     staff_code="ADMIN",
            #     login_datetime=login_time
            # )

            email_service = EmailNotificationService()
            email_service.send_login_alert(
                username=user.username,
                staff_code=user.staff_unique_id,
                login_datetime=login_time
            )


            refresh = RefreshToken.for_user(user)

            return Response({
                "message": "Admin login successful",
                "role": "ADMIN",
                "token": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }
            }, status=200)

        # ---------------------------------------------------
        # Invalid login_type
        # ---------------------------------------------------
        return Response(
            {"error": "Invalid login_type"},
            status=400
        )


