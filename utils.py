from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, date, time
from django.utils.timezone import make_aware, is_aware

def normalize_date(input_date: str | date | datetime, is_end: bool = False) -> datetime:

    if isinstance(input_date, str):
        input_date = datetime.strptime(input_date, "%Y-%m-%d")

    if isinstance(input_date, date) and not isinstance(input_date, datetime):
        input_date = datetime.combine(input_date, time.max if is_end else time.min)

    if not is_aware(input_date):
        input_date = make_aware(input_date)

    return input_date

def round_decimal(value, places=2):
    if not isinstance(value, Decimal):
        value = Decimal(str(value))  # Ensure value is a Decimal
    return value.quantize(Decimal(f'1.{"0"*places}'), rounding=ROUND_HALF_UP)
