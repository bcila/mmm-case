import csv
import hashlib
from io import TextIOWrapper
from rest_framework.exceptions import ValidationError
from django.db import transaction as db_transaction
from .models import Transaction, ImportBatch

CATEGORY_MAP = {
    "satış": "Sales",
    "fatura": "Utilities",
    "kira": "Rent",
    "yemek": "Food",
    "market": "Groceries",
}

def detect_category(description: str) -> str | None:
    desc_lower = description.lower()
    for keyword, category in CATEGORY_MAP.items():
        if keyword in desc_lower:
            return category
    return None

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
                    "date": row['date'],
                    "amount": row['amount'],
                    "currency": currency,
                    "transaction_type": row['type'],
                    "description": row['description'],
                    "category": category,
                }
            )
            
def get_filtered_transactions(user, start_date=None, end_date=None, type=None, category=None):

    qs = Transaction.objects.filter(user=user)
    if start_date:
        qs = qs.filter(date__gte=start_date)
    if end_date:
        qs = qs.filter(date__lte=end_date)
    if type:
        qs = qs.filter(type=type)
    if category:
        qs = qs.filter(category__iexact=category)
    return qs.order_by("-date")