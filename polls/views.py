from rest_framework import viewsets
from .models import Stock
from .serializers import StockSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from .rag.rag_chain import get_rag_answer
from django.http import StreamingHttpResponse
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet
from rest_framework.request import Request

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

class RagViewSet(ViewSet):
    @action(detail=False, methods=['post'])
    def ask(self, request: Request):
        question = request.data.get("question", "").strip()
        if not question:
            return StreamingHttpResponse(
                '{"error":"Question is required"}',
                status=400,
                content_type="application/json"
            )

        def stream():
            try:
                # get_rag_answer 返回生成器
                for chunk in get_rag_answer(question):
                    yield chunk
            except Exception as e:
                yield f"\nError: {str(e)}"

        return StreamingHttpResponse(stream(), content_type="text/plain")