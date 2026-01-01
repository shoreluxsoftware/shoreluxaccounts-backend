#staff_management/scheduler_jobs.py

import logging
from staff_management.booking_service import BookingService

logger = logging.getLogger(__name__)


def fetch_website_bookings_job():
    success, message = BookingService.fetch_website_bookings()
    if success:
        logger.info(message)
    else:
        logger.error(message)
