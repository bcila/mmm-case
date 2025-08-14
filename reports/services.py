from django.db.models import Sum
from transactions.models import Transaction

def calculate_kpi_summary(user, start_date=None, end_date=None):
    queryset = Transaction.objects.filter(user=user)
    if start_date:
        queryset = queryset.filter(date__gte=start_date)
    if end_date:
        queryset = queryset.filter(date__lte=end_date)

    # toplam gelir
    total_income = queryset.filter(type="credit").aggregate(total=Sum("amount"))["total"] or 0

    # toplam gider
    total_expense = queryset.filter(type="debit").aggregate(total=Sum("amount"))["total"] or 0
    total_expense = abs(total_expense)

    # net nakit akışı
    net_cash_flow = total_income - total_expense

    # en yüksek gider kategorileri
    expense_categories = (
        queryset.filter(type="debit", category__isnull=False)
        .values("category")
        .annotate(total=Sum("amount"))
        .order_by("total")[:5]
    )
    top_expense_categories = [
        {"category": e["category"], "total": abs(e["total"])}
        for e in expense_categories
    ]

    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "net_cash_flow": net_cash_flow,
        "top_expense_categories": top_expense_categories,
    }
