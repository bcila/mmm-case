import csv
import hashlib
from io import TextIOWrapper
from collections import Counter
from datetime import datetime, time
from rest_framework.exceptions import ValidationError
from django.utils.timezone import make_aware, is_aware
from django.db import transaction as db_transaction
from .models import Transaction, ImportBatch
from decimal import Decimal

# predefined categories with keywords
CATEGORY_KEYWORDS = {
    "Sales": ["satış", "fatura"],
    "Rent": ["kira"],
    "SaaS": ["saas", "crm", "aylık lisans"],
    "Office Supplies": ["kırtasiye", "ofis", "kalem", "defter"],
    "Payroll": ["maaş", "personel", "çalışan", "ücret"],
    "Utilities": ["elektrik", "su", "internet", "fatura"],
}

# predefined exchange rates for currency conversion
# could be fetched from an API in a real application
EXCHANGE_RATES = {
    'USD': Decimal('40.89'),
    'EUR': Decimal('47.81'),
    'TRY': Decimal('1'),
}

# could be change with ml/nlp model in future
def detect_category(description: str) -> str:
    desc_lower = description.lower()
    scores = Counter()

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in desc_lower:
                scores[category] += 1

    return scores.most_common(1)[0][0] if scores else "Uncategorized"

def validate_currency(value: str) -> str:
    value = value.strip().upper()
    if len(value) != 3 or not value.isalpha():
        raise ValidationError("Currency must be a 3-letter.")
    return value

def generate_unique_hash(user_id, row):
    hash_input = f"{user_id}-{row['date']}-{row['amount']}-{row['description']}"
    return hashlib.sha256(hash_input.encode()).hexdigest()

def import_transactions(user, csv_file, idempotency_key: str):
    if ImportBatch.objects.filter(idempotency_key=idempotency_key, user=user).exists():
        return False
    
    text_file = TextIOWrapper(csv_file, encoding='utf-8-sig')
    reader = csv.DictReader(text_file)

    with db_transaction.atomic():
        batch = ImportBatch.objects.create(user=user, idempotency_key=idempotency_key)

        for row in reader:
            currency = validate_currency(row['currency'])
            unique_hash = generate_unique_hash(user.id, row)
            category = detect_category(row['description'])

            Transaction.objects.get_or_create(
                unique_hash=unique_hash,
                defaults={
                    "user": user,
                    "batch": batch,
                    "date": make_aware(datetime.strptime(row['date'], "%Y-%m-%d")),
                    "amount": row['amount'],
                    "currency": currency,
                    "transaction_type": row['type'],
                    "description": row['description'],
                    "category": category,
                }
            )
            
def get_filtered_transactions(user, start_date=None, end_date=None, transaction_type=None, category=None):
    qs = Transaction.objects.filter(user=user)

    if start_date:
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        if not is_aware(start_date):
            start_date = make_aware(datetime.combine(start_date.date(), time.min))
        qs = qs.filter(date__gte=start_date)

    if end_date:
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        if not is_aware(end_date):
            end_date = make_aware(datetime.combine(end_date.date(), time.max))
        qs = qs.filter(date__lte=end_date)

    if transaction_type:
        qs = qs.filter(transaction_type=transaction_type)

    if category:
        qs = qs.filter(category__iexact=category)

    return qs.order_by("-date")


def convert_amount(amount: Decimal, from_currency: str, to_currency: str) -> Decimal:
    if from_currency == to_currency:
        return amount

    rate_from = EXCHANGE_RATES[from_currency]
    rate_to = EXCHANGE_RATES[to_currency]

    if from_currency == "TRY":
        return amount / rate_to

    if to_currency == "TRY":
        return amount * rate_from

    amount_in_try = amount * rate_from
    return amount_in_try / rate_to