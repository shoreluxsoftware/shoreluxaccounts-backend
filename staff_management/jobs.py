#staff_management/jobs.py
import logging
from datetime import timedelta
from django.utils import timezone
from django.core.cache import cache
from staff_management.models import Booking
from login.email_service import EmailNotificationService

logger = logging.getLogger(__name__)


def send_due_checkin_reminders():
    """
    Runs every few minutes.
    Sends reminder if:
    - Check-in is within next 6 hours
    - OR check-in time already passed
    """
    now = timezone.now()
    reminder_cutoff = now + timedelta(hours=6)

    bookings = Booking.objects.filter(
        checkin_date__lte=reminder_cutoff
    )

    email_service = EmailNotificationService()

    for booking in bookings:
        try:
            cache_key = f"checkin_reminder_sent_{booking.id}"

            if cache.get(cache_key):
                continue

            email_service.send_checkin_reminder(booking)
            cache.set(cache_key, True, timeout=60 * 60 * 24)

            logger.info(f"⏰ Check-in reminder sent for booking {booking.id}")

        except Exception as e:
            logger.error(f"Reminder failed for booking {booking.id}: {str(e)}")
