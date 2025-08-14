from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from reports.services import calculate_kpi_summary

class ReportSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        data = calculate_kpi_summary(request.user, start_date, end_date)
        return Response(data)