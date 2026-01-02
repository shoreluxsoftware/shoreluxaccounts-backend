
# =====================================================
# 1. login/views.py - UPDATED (NO CELERY)
# =====================================================

import logging
import time
import threading
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from admin_management.models import User
from login.email_service import EmailNotificationService

logger = logging.getLogger(__name__)


def send_email_async(email_type, **kwargs):
    def _send():
        logger.info(f"📧 Email thread started for {email_type}")
        try:
            email_service = EmailNotificationService()

            if email_type == "login_alert":
                email_service.send_login_alert(
                    username=kwargs.get('username'),
                    staff_code=kwargs.get('staff_code'),
                    login_datetime=kwargs.get('login_datetime')
                )

            logger.info(f"✅ Email thread finished for {email_type}")

        except Exception as e:
            logger.error(f"❌ Background email error ({email_type}): {str(e)}")

    thread = threading.Thread(target=_send)
    thread.start()


@method_decorator(csrf_exempt, name='dispatch')
class UnifiedLoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        start_time = time.time()
        logger.info(f"🔵 LOGIN REQUEST STARTED")
        
        login_type = request.data.get("login_type")
        username = request.data.get("username")
        password = request.data.get("password")
        staff_id = request.data.get("staff_unique_id")

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

        auth_start = time.time()
        user = authenticate(username=username, password=password)
        auth_time = time.time() - auth_start
        logger.info(f"⏱️ AUTHENTICATE took {auth_time:.2f}s")
        
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

            # ✅ Send login alert email in background (non-blocking)
            login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            send_email_async(
                email_type="login_alert",
                username=user.username,
                staff_code=user.staff_unique_id,
                login_datetime=login_time
            )

            token_start = time.time()
            logger.info(f"🟡 Generating tokens...")
            refresh = RefreshToken.for_user(user)
            token_time = time.time() - token_start
            logger.info(f"⏱️ Token generation took {token_time:.2f}s")

            total_time = time.time() - start_time
            logger.info(f"✅ STAFF LOGIN RESPONSE READY in {total_time:.2f}s")

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

            # ✅ Send login alert email in background (non-blocking)
            login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            send_email_async(
                email_type="login_alert",
                username=user.username,
                staff_code=user.staff_unique_id or "ADMIN",
                login_datetime=login_time
            )

            token_start = time.time()
            logger.info(f"🟡 Generating tokens...")
            refresh = RefreshToken.for_user(user)
            token_time = time.time() - token_start
            logger.info(f"⏱️ Token generation took {token_time:.2f}s")

            total_time = time.time() - start_time
            logger.info(f"✅ ADMIN LOGIN RESPONSE READY in {total_time:.2f}s")

            return Response({
                "message": "Admin login successful",
                "role": "ADMIN",
                "token": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }
            }, status=200)

        return Response(
            {"error": "Invalid login_type"},
            status=400
        )


# import logging
# import time
# from rest_framework.views import APIView
# from rest_framework.permissions import AllowAny
# from rest_framework.response import Response
# from django.contrib.auth import authenticate
# from rest_framework_simplejwt.tokens import RefreshToken
# from admin_management.models import User
# from datetime import datetime
# from django.views.decorators.csrf import csrf_exempt
# from django.utils.decorators import method_decorator
# from .email_service import EmailNotificationService

# logger = logging.getLogger(__name__)


# @method_decorator(csrf_exempt, name='dispatch')
# class UnifiedLoginAPIView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         start_time = time.time()
#         logger.info(f"🔵 LOGIN REQUEST STARTED")
        
#         login_type = request.data.get("login_type")
#         username = request.data.get("username")
#         password = request.data.get("password")
#         staff_id = request.data.get("staff_unique_id")

#         # Validate required fields
#         if not login_type:
#             return Response(
#                 {"error": "login_type is required (ADMIN or STAFF)"},
#                 status=400
#             )

#         if not username or not password:
#             return Response(
#                 {"error": "username and password are required"},
#                 status=400
#             )

#         # ⏱️ Authenticate user
#         auth_start = time.time()
#         user = authenticate(username=username, password=password)
#         auth_time = time.time() - auth_start
#         logger.info(f"⏱️ AUTHENTICATE took {auth_time:.2f}s")
        
#         if not user:
#             return Response(
#                 {"error": "Invalid username or password"},
#                 status=401
#             )

#         # ===================================================
#         # STAFF LOGIN
#         # ===================================================
#         if login_type == "STAFF":

#             if user.role != "STAFF":
#                 return Response(
#                     {"error": "This user is not a staff"},
#                     status=403
#                 )

#             if not user.can_login:
#                 return Response(
#                     {"error": "Login access not enabled for this staff"},
#                     status=403
#                 )

#             if not staff_id:
#                 return Response(
#                     {"error": "staff_unique_id is required for STAFF login"},
#                     status=400
#                 )

#             if user.staff_unique_id != staff_id:
#                 return Response(
#                     {"error": "Invalid staff ID"},
#                     status=401
#                 )

#             # ✅ Try to queue async email, fallback to sync if it fails
#             login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#             try:
#                 from .tasks import send_login_alert_email
#                 logger.info(f"🟡 Queueing async email task...")
#                 send_login_alert_email.delay(
#                     username=user.username,
#                     staff_code=user.staff_unique_id,
#                     login_datetime=login_time
#                 )
#                 logger.info(f"✅ Email task queued successfully")
#             except Exception as e:
#                 # Fallback to synchronous email if Celery fails
#                 logger.warning(f"⚠️ Celery unavailable, sending email synchronously: {str(e)}")
#                 try:
#                     email_service = EmailNotificationService()
#                     email_service.send_login_alert(
#                         username=user.username,
#                         staff_code=user.staff_unique_id,
#                         login_datetime=login_time
#                     )
#                 except Exception as email_error:
#                     logger.error(f"⚠️ Email sending failed (non-blocking): {str(email_error)}")

#             # Generate tokens
#             token_start = time.time()
#             logger.info(f"🟡 Generating tokens...")
#             refresh = RefreshToken.for_user(user)
#             token_time = time.time() - token_start
#             logger.info(f"⏱️ Token generation took {token_time:.2f}s")

#             total_time = time.time() - start_time
#             logger.info(f"✅ STAFF LOGIN RESPONSE READY in {total_time:.2f}s")

#             return Response({
#                 "message": "Staff login successful",
#                 "role": "STAFF",
#                 "staff_unique_id": user.staff_unique_id,
#                 "token": {
#                     "refresh": str(refresh),
#                     "access": str(refresh.access_token),
#                 }
#             }, status=200)

#         # ===================================================
#         # ADMIN LOGIN
#         # ===================================================
#         elif login_type == "ADMIN":

#             if user.role != "ADMIN":
#                 return Response(
#                     {"error": "This user is not an admin"},
#                     status=403
#                 )

#             # ✅ Try to queue async email, fallback to sync if it fails
#             login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#             try:
#                 from .tasks import send_login_alert_email
#                 logger.info(f"🟡 Queueing async email task...")
#                 send_login_alert_email.delay(
#                     username=user.username,
#                     staff_code=user.staff_unique_id or "ADMIN",
#                     login_datetime=login_time
#                 )
#                 logger.info(f"✅ Email task queued successfully")
#             except Exception as e:
#                 # Fallback to synchronous email if Celery fails
#                 logger.warning(f"⚠️ Celery unavailable, sending email synchronously: {str(e)}")
#                 try:
#                     email_service = EmailNotificationService()
#                     email_service.send_login_alert(
#                         username=user.username,
#                         staff_code=user.staff_unique_id or "ADMIN",
#                         login_datetime=login_time
#                     )
#                 except Exception as email_error:
#                     logger.error(f"⚠️ Email sending failed (non-blocking): {str(email_error)}")

#             # Generate tokens
#             token_start = time.time()
#             logger.info(f"🟡 Generating tokens...")
#             refresh = RefreshToken.for_user(user)
#             token_time = time.time() - token_start
#             logger.info(f"⏱️ Token generation took {token_time:.2f}s")

#             total_time = time.time() - start_time
#             logger.info(f"✅ ADMIN LOGIN RESPONSE READY in {total_time:.2f}s")

#             return Response({
#                 "message": "Admin login successful",
#                 "role": "ADMIN",
#                 "token": {
#                     "refresh": str(refresh),
#                     "access": str(refresh.access_token),
#                 }
#             }, status=200)

#         # Invalid login_type
#         return Response(
#             {"error": "Invalid login_type"},
#             status=400
#         )











# from rest_framework.views import APIView
# from rest_framework.permissions import AllowAny
# from rest_framework.response import Response
# from rest_framework import status
# from django.contrib.auth import authenticate
# from rest_framework_simplejwt.tokens import RefreshToken
# from admin_management.models import User

# from admin_management.models import *
# from admin_management.serializers import *
# from datetime import datetime
# # from login.sms_service import sms_service

# from .email_service import EmailNotificationService
# import logging
# import time
# from .tasks import send_login_alert_email  # ← Import async task

# logger = logging.getLogger(__name__)
# from django.views.decorators.csrf import csrf_exempt
# from django.utils.decorators import method_decorator

# # @method_decorator(csrf_exempt, name='dispatch')
# # class UnifiedLoginAPIView(APIView):
# #     permission_classes = [AllowAny]

# #     def post(self, request):
# #         login_type = request.data.get("login_type")   # ADMIN or STAFF
# #         username = request.data.get("username")
# #         password = request.data.get("password")
# #         staff_id = request.data.get("staff_unique_id")

# #         # ---------------------------------------------------
# #         # Validate required fields
# #         # ---------------------------------------------------
# #         if not login_type:
# #             return Response(
# #                 {"error": "login_type is required (ADMIN or STAFF)"},
# #                 status=400
# #             )

# #         if not username or not password:
# #             return Response(
# #                 {"error": "username and password are required"},
# #                 status=400
# #             )

# #         # ---------------------------------------------------
# #         # Authenticate credentials
# #         # ---------------------------------------------------
# #         user = authenticate(username=username, password=password)
# #         if not user:
# #             return Response(
# #                 {"error": "Invalid username or password"},
# #                 status=401
# #             )

# #         # ===================================================
# #         # STAFF LOGIN
# #         # ===================================================
# #         if login_type == "STAFF":

# #             if user.role != "STAFF":
# #                 return Response(
# #                     {"error": "This user is not a staff"},
# #                     status=403
# #                 )

# #             if not user.can_login:
# #                 return Response(
# #                     {"error": "Login access not enabled for this staff"},
# #                     status=403
# #                 )

# #             if not staff_id:
# #                 return Response(
# #                     {"error": "staff_unique_id is required for STAFF login"},
# #                     status=400
# #                 )

# #             if user.staff_unique_id != staff_id:
# #                 return Response(
# #                     {"error": "Invalid staff ID"},
# #                     status=401
# #                 )

# #             # Send login SMS
# #             login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# #             # sms_service.send_login_notification(
# #             #     username=user.username,
# #             #     staff_code=user.staff_unique_id,
# #             #     login_datetime=login_time
# #             # )

# #             email_service = EmailNotificationService()
# #             email_service.send_login_alert(
# #                 username=user.username,
# #                 staff_code=user.staff_unique_id,
# #                 login_datetime=login_time
# #             )


# #             refresh = RefreshToken.for_user(user)

# #             return Response({
# #                 "message": "Staff login successful",
# #                 "role": "STAFF",
# #                 "staff_unique_id": user.staff_unique_id,
# #                 "token": {
# #                     "refresh": str(refresh),
# #                     "access": str(refresh.access_token),
# #                 }
# #             }, status=200)

# #         # ===================================================
# #         # ADMIN LOGIN
# #         # ===================================================
# #         elif login_type == "ADMIN":

# #             if user.role != "ADMIN":
# #                 return Response(
# #                     {"error": "This user is not an admin"},
# #                     status=403
# #                 )

# #             # Admins do NOT need can_login
# #             login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# #             # sms_service.send_login_notification(
# #             #     username=user.username,
# #             #     staff_code="ADMIN",
# #             #     login_datetime=login_time
# #             # )

# #             email_service = EmailNotificationService()
# #             email_service.send_login_alert(
# #                 username=user.username,
# #                 staff_code=user.staff_unique_id,
# #                 login_datetime=login_time
# #             )


# #             refresh = RefreshToken.for_user(user)

# #             return Response({
# #                 "message": "Admin login successful",
# #                 "role": "ADMIN",
# #                 "token": {
# #                     "refresh": str(refresh),
# #                     "access": str(refresh.access_token),
# #                 }
# #             }, status=200)

# #         # ---------------------------------------------------
# #         # Invalid login_type
# #         # ---------------------------------------------------
# #         return Response(
# #             {"error": "Invalid login_type"},
# #             status=400
# #         )

# @method_decorator(csrf_exempt, name='dispatch')
# class UnifiedLoginAPIView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         start_time = time.time()
#         logger.info(f"🔵 LOGIN REQUEST STARTED")
        
#         login_type = request.data.get("login_type")
#         username = request.data.get("username")
#         password = request.data.get("password")
#         staff_id = request.data.get("staff_unique_id")

#         # Validate required fields
#         if not login_type:
#             return Response(
#                 {"error": "login_type is required (ADMIN or STAFF)"},
#                 status=400
#             )

#         if not username or not password:
#             return Response(
#                 {"error": "username and password are required"},
#                 status=400
#             )

#         # ⏱️ Authenticate user
#         auth_start = time.time()
#         user = authenticate(username=username, password=password)
#         auth_time = time.time() - auth_start
#         logger.info(f"⏱️ AUTHENTICATE took {auth_time:.2f}s")
        
#         if not user:
#             return Response(
#                 {"error": "Invalid username or password"},
#                 status=401
#             )

#         # ===================================================
#         # STAFF LOGIN
#         # ===================================================
#         if login_type == "STAFF":

#             if user.role != "STAFF":
#                 return Response(
#                     {"error": "This user is not a staff"},
#                     status=403
#                 )

#             if not user.can_login:
#                 return Response(
#                     {"error": "Login access not enabled for this staff"},
#                     status=403
#                 )

#             if not staff_id:
#                 return Response(
#                     {"error": "staff_unique_id is required for STAFF login"},
#                     status=400
#                 )

#             if user.staff_unique_id != staff_id:
#                 return Response(
#                     {"error": "Invalid staff ID"},
#                     status=401
#                 )

#             # ✅ Queue email in background (non-blocking)
#             login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#             logger.info(f"🟡 Queueing email task...")
#             send_login_alert_email.delay(
#                 username=user.username,
#                 staff_code=user.staff_unique_id,
#                 login_datetime=login_time
#             )
#             logger.info(f"✅ Email task queued")

#             # Generate tokens
#             token_start = time.time()
#             logger.info(f"🟡 Generating tokens...")
#             refresh = RefreshToken.for_user(user)
#             token_time = time.time() - token_start
#             logger.info(f"⏱️ Token generation took {token_time:.2f}s")

#             total_time = time.time() - start_time
#             logger.info(f"✅ STAFF LOGIN RESPONSE READY in {total_time:.2f}s")

#             return Response({
#                 "message": "Staff login successful",
#                 "role": "STAFF",
#                 "staff_unique_id": user.staff_unique_id,
#                 "token": {
#                     "refresh": str(refresh),
#                     "access": str(refresh.access_token),
#                 }
#             }, status=200)

#         # ===================================================
#         # ADMIN LOGIN
#         # ===================================================
#         elif login_type == "ADMIN":

#             if user.role != "ADMIN":
#                 return Response(
#                     {"error": "This user is not an admin"},
#                     status=403
#                 )

#             # ✅ Queue email in background (non-blocking)
#             login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#             logger.info(f"🟡 Queueing email task...")
#             send_login_alert_email.delay(
#                 username=user.username,
#                 staff_code=user.staff_unique_id,
#                 login_datetime=login_time
#             )
#             logger.info(f"✅ Email task queued")

#             # Generate tokens
#             token_start = time.time()
#             logger.info(f"🟡 Generating tokens...")
#             refresh = RefreshToken.for_user(user)
#             token_time = time.time() - token_start
#             logger.info(f"⏱️ Token generation took {token_time:.2f}s")

#             total_time = time.time() - start_time
#             logger.info(f"✅ ADMIN LOGIN RESPONSE READY in {total_time:.2f}s")

#             return Response({
#                 "message": "Admin login successful",
#                 "role": "ADMIN",
#                 "token": {
#                     "refresh": str(refresh),
#                     "access": str(refresh.access_token),
#                 }
#             }, status=200)

#         # Invalid login_type
#         return Response(
#             {"error": "Invalid login_type"},
#             status=400
#         )
