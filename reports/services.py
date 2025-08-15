from django.db.models import Sum
from transactions.models import Transaction
from datetime import datetime, time
from django.utils.timezone import make_aware, is_aware
from django.db.models import Sum
from transactions.services import convert_amount
from utils import round_decimal

def calculate_kpi_summary(user, start_date=None, end_date=None, target_currency="TRY"):
    queryset = Transaction.objects.filter(user=user)

    # timezone-aware date filtering
    if start_date:
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        if not is_aware(start_date):
            start_date = make_aware(datetime.combine(start_date.date(), time.min))
        queryset = queryset.filter(date__gte=start_date)

    if end_date:
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        if not is_aware(end_date):
            end_date = make_aware(datetime.combine(end_date.date(), time.max))
        queryset = queryset.filter(date__lte=end_date)

    # total income, expense and net cash flow calculations 
    total_income = 0
    total_expense = 0
    category_totals = {}

    for tx in queryset:
        amount_converted = convert_amount(tx.amount, tx.currency, target_currency)
        if tx.amount > 0:
            total_income += amount_converted
        else:
            total_expense += abs(amount_converted)
            if tx.category:
                category_totals[tx.category] = category_totals.get(tx.category, 0) + abs(amount_converted)

    net_cash_flow = total_income - total_expense

    # top 5 expense categories
    top_expense_categories = sorted(
        [
            {"category": k, "total": round_decimal(v)}
            for k, v in category_totals.items()
        ],
        key=lambda x: x["total"],
        reverse=True
    )[:5]

    return {
        "total_income": round_decimal(total_income),
        "total_expense": round_decimal(total_expense),
        "net_cash_flow": round_decimal(net_cash_flow),
        "top_expense_categories": top_expense_categories,
        "currency": target_currency,
    }