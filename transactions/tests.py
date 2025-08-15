import pytest
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.models import User
from transactions.models import Transaction, ImportBatch
from transactions.services import get_filtered_transactions
from transactions.services import detect_category

@pytest.fixture
def users_and_transactions(db):
    user = User.objects.create_user(username="testuser", password="pass1234")
    other_user = User.objects.create_user(username="otheruser", password="pass1234")
    batch = ImportBatch.objects.create(user=user, idempotency_key="batch-key")

    Transaction.objects.create(
        user=user, batch=batch, date=timezone.make_aware(datetime(2025, 7, 1)),
        amount=4500.00, currency="TRY", transaction_type="credit",
        description="Satış: Fatura #1023", category="Sales", unique_hash="hash1"
    )
    Transaction.objects.create(
        user=user, batch=batch, date=timezone.make_aware(datetime(2025, 7, 1)),
        amount=-1200.00, currency="TRY", transaction_type="debit",
        description="Kira Ödemesi", category="Rent", unique_hash="hash2"
    )
    Transaction.objects.create(
        user=user, batch=batch, date=timezone.make_aware(datetime(2025, 7, 1)),
        amount=-500.00, currency="TRY", transaction_type="debit",
        description="Yemek Gideri", category="Food", unique_hash="hash3"
    )

    other_batch = ImportBatch.objects.create(user=other_user, idempotency_key="other-key")
    Transaction.objects.create(
        user=other_user, batch=other_batch, date=timezone.make_aware(datetime(2025, 7, 1)),
        amount=1000.00, currency="TRY", transaction_type="credit",
        description="Başka kullanıcı", category="Other", unique_hash="hash4"
    )
    return user

def test_returns_only_user_transactions(users_and_transactions):
    user = users_and_transactions
    qs = get_filtered_transactions(user)
    assert qs.count() == 3

def test_filters_by_date_range(users_and_transactions):
    user = users_and_transactions
    qs = get_filtered_transactions(user, start_date="2025-07-01", end_date="2025-07-31")
    assert qs.count() == 3

def test_filters_by_type(users_and_transactions):
    user = users_and_transactions
    qs = get_filtered_transactions(user, transaction_type="credit")
    assert qs.count() == 1
    assert qs.first().transaction_type == "credit"

def test_filters_by_category(users_and_transactions):
    user = users_and_transactions
    qs = get_filtered_transactions(user, category="Rent")
    assert qs.count() == 1
    assert qs.first().category == "Rent"

def test_combined_filters(users_and_transactions):
    user = users_and_transactions
    qs = get_filtered_transactions(user, start_date="2025-07-01", transaction_type="debit")
    assert qs.count() == 2

    # to make sure which description first, better sort explicitly:
    first_desc = qs.order_by("description").first().description
    assert first_desc in ["Kira Ödemesi", "Yemek Gideri"]

def test_category_defaults_to_uncategorized():
    assert detect_category("Bilinmeyen bir açıklama") == "Uncategorized"
