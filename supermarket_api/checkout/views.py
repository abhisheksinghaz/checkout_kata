from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import models
from django.utils import timezone

from .models import Product, Promotion, Cart, CartItem
from .serializers import (
    ProductSerializer, PromotionSerializer, PromotionCreateSerializer,
    CartSerializer, ScanItemSerializer, CheckoutResponseSerializer
)
from .services import CheckoutService, PricingEngine


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Product operations

    list: Get all products
    retrieve: Get a specific product
    create: Create a new product
    update: Update a product
    partial_update: Partially update a product
    destroy: Delete a product
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'product_id'

    @action(detail=True, methods=['get'])
    def promotions(self, request, product_id=None):
        """Get active promotions for a product"""
        product = self.get_object()
        promotions = Promotion.objects.filter(
            product=product,
            active=True,
            start_date__lte=timezone.now()
        ).filter(
            models.Q(end_date__isnull=True) | models.Q(end_date__gte=timezone.now())
        )

        serializer = PromotionSerializer(promotions, many=True)
        return Response({
            'product_id': product_id,
            'promotions': serializer.data,
            'count': promotions.count()
        })


class PromotionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Promotion operations

    list: Get all promotions
    retrieve: Get a specific promotion
    create: Create a new promotion
    update: Update a promotion
    partial_update: Partially update a promotion
    destroy: Delete a promotion
    """
    queryset = Promotion.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return PromotionCreateSerializer
        return PromotionSerializer

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a promotion"""
        promotion = self.get_object()
        promotion.active = False
        promotion.save()

        serializer = self.get_serializer(promotion)
        return Response({
            'message': f'Promotion {pk} deactivated successfully',
            'promotion': serializer.data
        })

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a promotion"""
        promotion = self.get_object()
        promotion.active = True
        promotion.save()

        serializer = self.get_serializer(promotion)
        return Response({
            'message': f'Promotion {pk} activated successfully',
            'promotion': serializer.data
        })


class CheckoutAPIView(APIView):
    """
    API for checkout operations
    """

    def get_session_id(self, request):
        """Get or create session ID"""
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
        return session_id

    def get(self, request):
        """Get current cart"""
        session_id = self.get_session_id(request)
        cart = CheckoutService.get_or_create_cart(session_id)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def scan(self, request):
        """Scan an item and add to cart"""
        session_id = self.get_session_id(request)
        cart = CheckoutService.get_or_create_cart(session_id)

        serializer = ScanItemSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        product_id = serializer.validated_data['product_id']
        product = Product.objects.get(product_id=product_id)

        # Add item to cart
        CartItem.objects.create(cart=cart, product=product)

        return Response({
            'success': True,
            'message': f'Added {product.name} to cart',
            'product': ProductSerializer(product).data,
            'cart_total_items': cart.items.count()
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def remove(self, request):
        """Remove one instance of an item from cart"""
        session_id = self.get_session_id(request)
        cart = CheckoutService.get_or_create_cart(session_id)

        product_id = request.data.get('product_id')
        if not product_id:
            return Response(
                {'error': 'product_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Remove one instance
        item = cart.items.filter(product__product_id=product_id).first()
        if item:
            item.delete()
            return Response({
                'success': True,
                'message': f'Removed {product_id} from cart',
                'cart_total_items': cart.items.count()
            })

        return Response(
            {'error': 'Item not found in cart'},
            status=status.HTTP_404_NOT_FOUND
        )

    @action(detail=False, methods=['post'])
    def calculate(self, request):
        """Calculate total with promotions"""
        session_id = self.get_session_id(request)
        cart = CheckoutService.get_or_create_cart(session_id)

        result = CheckoutService.calculate_cart_total(cart)

        serializer = CheckoutResponseSerializer(data=result)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def clear(self, request):
        """Clear cart"""
        session_id = self.get_session_id(request)
        cart = CheckoutService.get_or_create_cart(session_id)
        cart.clear()

        return Response({
            'success': True,
            'message': 'Cart cleared successfully'
        })


# Additional view for scanning (alternative endpoint)
class ScanItemView(APIView):
    """Scan item endpoint"""

    def post(self, request):
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key

        cart = CheckoutService.get_or_create_cart(session_id)

        serializer = ScanItemSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        product_id = serializer.validated_data['product_id']
        product = Product.objects.get(product_id=product_id)

        CartItem.objects.create(cart=cart, product=product)

        return Response({
            'success': True,
            'message': f'Added {product.name} to cart',
            'product': ProductSerializer(product).data,
            'cart_total_items': cart.items.count()
        }, status=status.HTTP_201_CREATED)


class CalculateTotalView(APIView):
    """Calculate total endpoint"""

    def get(self, request):
        session_id = request.session.session_key
        if not session_id:
            return Response({
                'total': 0,
                'item_count': 0,
                'breakdown': [],
                'total_savings': 0
            })

        cart = CheckoutService.get_or_create_cart(session_id)
        result = CheckoutService.calculate_cart_total(cart)

        return Response(result)