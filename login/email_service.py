
# login/email_service.py

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class EmailNotificationService:

    def __init__(self):
        config = sib_api_v3_sdk.Configuration()
        config.api_key['api-key'] = settings.BREVO_API_KEY

        self.client = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(config)
        )

    def send_email(self, subject, message):
        try:
            email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": settings.ALERT_EMAIL}],
                sender={"email": settings.DEFAULT_FROM_EMAIL, "name": "Shorel ux"},
                subject=subject,
                text_content=message,
            )

            self.client.send_transac_email(email)
            logger.info(f"📧 Email sent via Brevo API: {subject}")

        except ApiException as e:
            logger.error(f"❌ Brevo API error: {e}")



# import logging
# from django.core.mail import send_mail
# from django.conf import settings

# logger = logging.getLogger(__name__)


# class EmailNotificationService:

#     def send_email(self, subject, message):
#         try:
#             send_mail(
#                 subject=subject,
#                 message=message,
#                 from_email=settings.DEFAULT_FROM_EMAIL,
#                 recipient_list=[settings.ALERT_EMAIL],
#                 fail_silently=False
#             )
#             logger.info(f"📧 Email sent: {subject}")
#             return {"success": True}

#         except Exception as e:
#             logger.error(f"❌ Email failed: {str(e)}")
#             return {"success": False, "error": str(e)}

#     def send_login_alert(self, username, staff_code, login_datetime):
#         subject = "🔐 Login Alert - Shorelux"
#         message = f"""
# LOGIN ALERT

# User: {username}
# Staff Code: {staff_code}
# Login Time: {login_datetime}
# """
#         return self.send_email(subject, message)

#     def send_otp_email(self, otp, verification_type, username):
#         subject = "🔑 OTP Verification - Shorelux"
#         message = f"""
# OTP VERIFICATION

# User: {username}
# Action: {verification_type}
# OTP: {otp}

# Valid for 10 minutes
# """
#         return self.send_email(subject, message)

#     def send_checkin_reminder(self, booking):
#         subject = "⏰ Check-in Reminder (6 Hours)"
#         message = f"""
# CHECK-IN REMINDER

# Guest: {booking.guest_name}
# Room: {booking.room_no}
# Check-in: {booking.checkin_date}
# Phone: {booking.phone_number}
# Amount: ₹{booking.booking_price}
# """
#         return self.send_email(subject, message)



# import logging
# from django.core.mail import send_mail
# from django.conf import settings

# logger = logging.getLogger(__name__)

# class EmailNotificationService:

#     def send_email(self, subject, message):
#         try:
#             send_mail(
#                 subject=subject,
#                 message=message,
#                 from_email=settings.DEFAULT_FROM_EMAIL,
#                 recipient_list=[settings.ALERT_EMAIL],
#                 fail_silently=False
#             )
#             logger.info(f"Email sent: {subject}")
#             return {"success": True}

#         except Exception as e:
#             logger.error(f"Email failed: {str(e)}")
#             return {"success": False, "error": str(e)}

#     # -----------------------------
#     # LOGIN ALERT
#     # -----------------------------
#     def send_login_alert(self, username, staff_code, login_datetime):
#         subject = "🔐 Login Alert - Shorelux"

#         message = f"""
# LOGIN ALERT

# User: {username}
# Staff Code: {staff_code}
# Login Time: {login_datetime}

# If this was not you, please investigate immediately.
#         """

#         return self.send_email(subject, message)

#     # -----------------------------
#     # OTP EMAIL
#     # -----------------------------
#     def send_otp_email(self, otp, verification_type, username):
#         subject = "🔑 OTP Verification - Shorelux"

#         message = f"""
# OTP VERIFICATION

# User: {username}
# Action: {verification_type.replace('_', ' ').title()}
# OTP: {otp}

# Valid for: 10 minutes
# Do not share this OTP.
#         """

#         return self.send_email(subject, message)

#     # -----------------------------
#     # CHECK-IN REMINDER
#     # -----------------------------
#     def send_checkin_reminder(self, booking):
#         subject = "⏰ Check-in Reminder (6 Hours)"

#         message = f"""
# CHECK-IN REMINDER

# Guest: {booking.guest_name}
# Room: {booking.room_no}
# Check-in Date: {booking.checkin_date}
# Phone: {booking.phone_number}
# Amount: ₹{booking.booking_price}

# This is a 6-hour advance reminder.
#         """

#         return self.send_email(subject, message)
