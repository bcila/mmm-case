import pytest
from datetime import datetime
from django.utils.timezone import make_aware
from django.contrib.auth.models import User
from transactions.models import Transaction, ImportBatch
from reports.services import calculate_kpi_summary

@pytest.fixture
def user_with_transactions(db):
    user = User.objects.create_user(username="reportuser", password="pass1234")
    batch = ImportBatch.objects.create(user=user, idempotency_key="report-key")

    Transaction.objects.create(
        user=user, batch=batch, date=make_aware(datetime(2025, 7, 1)),
        amount=4500.00, currency="TRY", transaction_type="credit",
        description="Satış: Fatura #1023", category="Sales", unique_hash="hash_report1"
    )
    Transaction.objects.create(
        user=user, batch=batch, date=make_aware(datetime(2025, 7, 2)),
        amount=-1200.00, currency="TRY", transaction_type="debit",
        description="Kira Ödemesi", category="Rent", unique_hash="hash_report2"
    )
    Transaction.objects.create(
        user=user, batch=batch, date=make_aware(datetime(2025, 7, 3)),
        amount=-800.00, currency="TRY", transaction_type="debit",
        description="Market Harcaması", category="Food", unique_hash="hash_report3"
    )
    return user

def test_calculates_totals_correctly(user_with_transactions):
    summary = calculate_kpi_summary(user_with_transactions)
    assert summary["total_income"] == 4500.00
    assert summary["total_expense"] == 2000.00  # abs(-1200) + abs(-800)
    assert summary["net_cash_flow"] == 2500.00

def test_top_expense_categories_sorted(user_with_transactions):
    summary = calculate_kpi_summary(user_with_transactions)
    top = summary["top_expense_categories"]
    assert len(top) == 2
    totals = [c["total"] for c in top]
    assert totals == sorted(totals, reverse=True)

def test_date_range_filter(user_with_transactions):
    summary = calculate_kpi_summary(
        user_with_transactions,
        start_date="2025-08-01",
        end_date="2025-08-31"
    )
    assert summary["total_income"] == 0
    assert summary["total_expense"] == 0
    assert summary["net_cash_flow"] == 0
    assert summary["top_expense_categories"] == []
