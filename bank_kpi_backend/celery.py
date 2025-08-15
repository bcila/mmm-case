import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bank_kpi_backend.settings')

app = Celery('bank_kpi_backend')
app.config_from_object('django.conf:settings', namespace='CELERY')

# auto-discover tasks
app.autodiscover_tasks()

# schedule configuration
app.conf.beat_schedule = {
    'generate-weekly-reports-every-monday-morning': {
        'task': 'reports.tasks.generate_weekly_reports',
        'schedule': crontab(hour=8, minute=0, day_of_week=1),  # Monday at 08:00
    },
}