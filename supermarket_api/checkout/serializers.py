from rest_framework import serializers
from .models import Product, Promotion, Cart, CartItem

class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model"""

    class Meta:
        model = Product
        fields = ['product_id', 'name', 'unit_price', 'active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class PromotionSerializer(serializers.ModelSerializer):
    """Serializer for Promotion model"""
    product_id = serializers.CharField(source='product.product_id', read_only=True)
    is_active_now = serializers.SerializerMethodField()

    class Meta:
        model = Promotion
        fields = [
            'id', 'product_id', 'promotion_type', 'promotion_data',
            'start_date', 'end_date', 'priority', 'active',
            'is_active_now', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_is_active_now(self, obj):
        return obj.is_active_now()


class PromotionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating promotions"""
    product_id = serializers.CharField(write_only=True)

    class Meta:
        model = Promotion
        fields = [
            'product_id', 'promotion_type', 'promotion_data',
            'start_date', 'end_date', 'priority', 'active'
        ]

    def validate_product_id(self, value):
        """Validate product exists"""
        try:
            Product.objects.get(product_id=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError(f"Product {value} does not exist")
        return value

    def create(self, validated_data):
        product_id = validated_data.pop('product_id')
        product = Product.objects.get(product_id=product_id)
        validated_data['product'] = product
        return super().create(validated_data)


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for CartItem"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    unit_price = serializers.DecimalField(
        source='product.unit_price',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_name', 'unit_price', 'added_at']
        read_only_fields = ['added_at']


class CartSerializer(serializers.ModelSerializer):
    """Serializer for Cart"""
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['session_id', 'items', 'total_items', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def get_total_items(self, obj):
        return obj.items.count()


class ScanItemSerializer(serializers.Serializer):
    """Serializer for scanning items"""
    product_id = serializers.CharField(max_length=10)

    def validate_product_id(self, value):
        try:
            product = Product.objects.get(product_id=value)
            if not product.active:
                raise serializers.ValidationError("Product is not available")
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found")
        return value


class CheckoutResponseSerializer(serializers.Serializer):
    """Serializer for checkout response"""
    total = serializers.FloatField()
    item_count = serializers.IntegerField()
    breakdown = serializers.ListField()
    total_savings = serializers.FloatField()