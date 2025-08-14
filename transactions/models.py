from django.db import models
from django.conf import settings

class ImportBatch(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    idempotency_key = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.idempotency_key}"

class Transaction(models.Model):
    CREDIT = 'credit'
    DEBIT = 'debit'
    TRANSACTION_TYPE_CHOICES = [
        (CREDIT, 'Credit'),
        (DEBIT, 'Debit'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateTimeField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3)
    transaction_type = models.CharField(max_length=6, choices=TRANSACTION_TYPE_CHOICES)
    description = models.TextField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    unique_hash = models.CharField(max_length=64, unique=True)
    batch = models.ForeignKey(ImportBatch, on_delete=models.CASCADE, related_name="transactions", default=1)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'date']),
        ]

    def __str__(self):
        return f"{self.user} - {self.date} - {self.amount} {self.currency}"
    