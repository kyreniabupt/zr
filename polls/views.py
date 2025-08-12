from rest_framework import viewsets
from .models import Stock
from .serializers import StockSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from .rag.rag import get_rag_answer
from rest_framework.decorators import action
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.parsers import JSONParser
from django.http import StreamingHttpResponse

class StockPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 3000

class get_all_stocks(viewsets.ModelViewSet):
    serializer_class = StockSerializer
    pagination_class = StockPagination

    def get_queryset(self):
        queryset = Stock.objects.all().order_by('date')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        return queryset

class RagViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    parser_classes = [JSONParser]

    @action(detail=False, methods=["post"])
    def chat(self, request):
        user_message = request.data.get("message")
        if not user_message:
            return Response({"error": "Missing 'message' field"}, status=400)

        def stream():

            for chunk in get_rag_answer(user_message):
                yield chunk

        return StreamingHttpResponse(stream(), content_type="text/plain")
