from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import get_all_stocks

router = DefaultRouter()
router.register(r'stocks', get_all_stocks,basename='stocks')

urlpatterns = [
    path('', include(router.urls)),
]