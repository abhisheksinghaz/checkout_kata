from django.contrib import admin
from .models import Product, Promotion, Cart, CartItem

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_id', 'name', 'unit_price', 'active', 'created_at']
    list_filter = ['active', 'created_at']
    search_fields = ['product_id', 'name']


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'promotion_type', 'priority', 'active', 'start_date', 'end_date']
    list_filter = ['promotion_type', 'active', 'start_date']
    search_fields = ['product__product_id', 'product__name']


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'created_at', 'updated_at']
    inlines = [CartItemInline]