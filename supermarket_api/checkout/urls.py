from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewSet, PromotionViewSet, CheckoutAPIView,
    ScanItemView, CalculateTotalView
)

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'promotions', PromotionViewSet, basename='promotion')

urlpatterns = [
    path('', include(router.urls)),

    # Checkout endpoints
    path('checkout/', CheckoutAPIView.as_view(), name='checkout'),
    path('checkout/scan/', ScanItemView.as_view(), name='scan-item'),
    path('checkout/calculate/', CalculateTotalView.as_view(), name='calculate-total'),
]