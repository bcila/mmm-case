from rest_framework import status, permissions, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes, OpenApiRequest
from .services import import_transactions
from .serializers import MessageResponseSerializer, TransactionUploadSerializer, TransactionSerializer
from .services import get_filtered_transactions

class TransactionUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serialization_class = TransactionUploadSerializer
    parser_classes = [MultiPartParser]
    @extend_schema(
        request=TransactionUploadSerializer,
        responses={201: MessageResponseSerializer},
        parameters=[
            OpenApiParameter(name='Idempotency-Key', description='Unique key to prevent duplicate uploads', required=True, type=OpenApiTypes.STR, location=OpenApiParameter.HEADER),
        ]
    )
    def post(self, request, *args, **kwargs):
        csv_file = request.FILES.get("file")
        idempotency_key = request.headers.get("Idempotency-Key")

        if not idempotency_key:
            raise ValidationError("Idempotency-Key header is required")
        if not csv_file:
            return Response({"error": "CSV file is required"}, status=status.HTTP_400_BAD_REQUEST)

        created = import_transactions(request.user, csv_file, idempotency_key)
        if not created:
            return Response({"message": "This upload has already been processed"}, status=status.HTTP_200_OK)
        
        return Response({"message": "Transactions uploaded successfully"}, status=status.HTTP_201_CREATED)
    
class TransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        user = self.request.user
        params = self.request.query_params
        return get_filtered_transactions(
            user=user,
            start_date=params.get("start_date"),
            end_date=params.get("end_date"),
            type=params.get("type"),
            category=params.get("category"),
        )