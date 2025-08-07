from rest_framework import viewsets
from .models import Stock
from .serializers import StockSerializer
from rest_framework.pagination import PageNumberPagination

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

