from django.contrib import admin
from orders.models import Order, OrderItem, OrderAddress


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'total_amount', 'order_status', 'created_at')
    search_fields = ('order_number', 'user__username')
    list_filter = ('order_status', 'created_at')
    readonly_fields = ('order_number', 'created_at', 'updated_at')
    fieldsets = (
        ('Order Information', {'fields': ('order_number', 'user', 'total_amount', 'order_status')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')
    search_fields = ('order__order_number', 'product__name')


@admin.register(OrderAddress)
class OrderAddressAdmin(admin.ModelAdmin):
    list_display = ('order', 'full_name', 'city', 'state')
    search_fields = ('order__order_number', 'full_name', 'city')
