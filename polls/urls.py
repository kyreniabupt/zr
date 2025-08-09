# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import get_all_stocks, RagViewSet  

router = DefaultRouter()
router.register(r'stocks', get_all_stocks, basename='stocks')
router.register(r'rag', RagViewSet, basename='rag')  

urlpatterns = [
    path('', include(router.urls)),
]