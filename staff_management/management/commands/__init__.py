from django.core.management.base import BaseCommand
from staff_management.booking_service import BookingService


class Command(BaseCommand):
    help = 'Fetch bookings from website API and store them'

    def handle(self, *args, **options):
        success, message = BookingService.fetch_website_bookings()
        
        if success:
            self.stdout.write(self.style.SUCCESS(f"✅ {message}"))
        else:
            self.stdout.write(self.style.ERROR(f"❌ {message}"))