from rest_framework import serializers
from .models import Transaction

class MessageResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    
class TransactionUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"
        read_only_fields = ("user", "unique_hash", "batch")