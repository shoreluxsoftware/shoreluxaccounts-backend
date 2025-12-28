
# =============================================
# staff_management/tasks.py (Celery Tasks)
# =============================================

import logging
from celery import shared_task
from django.utils import timezone
from datetime import timedelta

from .models import Booking
from login.email_service import EmailNotificationService

logger = logging.getLogger(__name__)


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3, "countdown": 60})
def schedule_booking_reminder(self, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)

        reminder_datetime = booking.checkin_date - timedelta(hours=6)
        now = timezone.now()

        if reminder_datetime > now:
            logger.info(f"⏰ Scheduling EMAIL reminder for booking {booking_id}")

            send_checkin_reminder_email.apply_async(
                args=[booking_id],
                eta=reminder_datetime
            )
        else:
            logger.info("⏳ Reminder time passed, sending EMAIL immediately")
            EmailNotificationService().send_checkin_reminder(booking)

    except Booking.DoesNotExist:
        logger.error(f"❌ Booking {booking_id} not found")


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3, "countdown": 60})
def send_checkin_reminder_email(self, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)
        logger.info(f"📧 Sending 6-hour reminder EMAIL for booking {booking_id}")

        result = EmailNotificationService().send_checkin_reminder(booking)

        if result.get("success"):
            logger.info("✅ Email reminder sent successfully")
        else:
            logger.error(f"❌ Email failed: {result.get('error')}")

    except Booking.DoesNotExist:
        logger.error(f"❌ Booking {booking_id} not found")




#------------ WEBSITE BOOKING FETCH ----------#


import requests
from celery import shared_task
from datetime import datetime
from decimal import Decimal

from .models import Booking
from django.conf import settings


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=30, retry_kwargs={"max_retries": 5})
def fetch_website_bookings(self):
    """
    Fetch bookings from website API and store them automatically.
    """

    url = settings.WEBSITE_BOOKING_API_URL
    params = {
        "api_key": settings.WEBSITE_API_KEY
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    payload = response.json()

    bookings = payload.get("bookings", [])

    for b in bookings:
        website_item_id = str(b["item_id"])

        # ❌ Already exists → skip
        if Booking.objects.filter(website_item_id=website_item_id).exists():
            continue

        checkin = datetime.strptime(b["Checkin_Date"], "%d/%m/%Y")
        checkout = datetime.strptime(b["Checkout_Date"], "%d/%m/%Y")

        total_cost = Decimal(b["Total_Cost"])
        
        Booking.objects.create(
            website_item_id=website_item_id,
            source=1,  # WEBSITE
            booking_date=checkin.date(),
            guest_name=b.get("Customer_Name"),
            room_no=None,              # ✅ DO NOT MAP Room_Type
            phone_number=b.get("Customer_Phone"),
            booking_type=None,         # ✅ DO NOT MAP Room_Type
            checkin_date=checkin,
            checkout_date=checkout,
            booking_price=total_cost,
            paid_amount=Decimal("0.00"),
            pending_amount=total_cost
        )


    return f"Fetched {len(bookings)} website bookings"