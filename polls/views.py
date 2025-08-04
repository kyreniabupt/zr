from rest_framework import viewsets
from .models import Stock
from .serializers import StockSerializer
from rest_framework.pagination import PageNumberPagination

class StockPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'  # 支持客户端指定每页大小
    max_page_size = 1000

class get_all_stocks(viewsets.ModelViewSet):
    queryset = Stock.objects.all().order_by('-date')
    serializer_class = StockSerializer
    pagination_class = StockPagination