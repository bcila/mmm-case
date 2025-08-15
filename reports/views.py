from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from reports.services import calculate_kpi_summary
from drf_spectacular.utils import extend_schema, OpenApiParameter

class ReportSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter("start_date", str, description="Filter summary from this date (YYYY-MM-DD)", required=False),
            OpenApiParameter("end_date", str, description="Filter summary up to this date (YYYY-MM-DD)", required=False),
            OpenApiParameter("currency", str, description="Target currency for report totals (e.g. TRY, USD, EUR)", required=False
        ),
        ],
        description="Get KPI summary report for the authenticated user.",
        responses={200: dict}
    )
    def get(self, request):
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        currency = request.query_params.get("currency") or "TRY"

        data = calculate_kpi_summary(request.user, start_date, end_date, currency)
        return Response(data)