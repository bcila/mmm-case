from django.urls import path
from .views import TransactionUploadView, TransactionListView

urlpatterns = [
    path('upload/', TransactionUploadView.as_view(), name='transaction-upload'),
    path('', TransactionListView.as_view(), name='transaction-list'),
]