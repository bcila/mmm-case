from celery import shared_task
from django.contrib.auth import get_user_model
from reports.services import calculate_kpi_summary
from datetime import timedelta, datetime
from django.utils.timezone import now
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

@shared_task
def generate_weekly_reports():
    today = now().date()
    start_date = today - timedelta(days=7)
    end_date = today

    for user in User.objects.all():
        try:
            summary = calculate_kpi_summary(user, start_date=start_date, end_date=end_date, target_currency="TRY")
            logger.info(f"Weekly report for {user.email or user.username}: {summary}")
            # at this point we can save the summary to a model or send it via email
        except Exception as e:
            logger.error(f"Failed to generate report for {user}: {e}")
