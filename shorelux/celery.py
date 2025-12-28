#=============================================
# shorelux/celery.py (Celery Configuration - In project root)
# =============================================

import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shorelux.settings')

app = Celery('shorelux')

# Load configuration from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks
app.autodiscover_tasks()

# Periodic tasks (if needed)
app.conf.beat_schedule = {
    # You can add periodic tasks here if needed
    # Example: Send daily report at 8 AM
    'send-daily-report': {
        'task': 'staff_management.tasks.send_daily_report',
        'schedule': crontab(hour=2, minute=0),
    },
}
