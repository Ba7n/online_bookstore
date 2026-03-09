from django.contrib import admin
from payments.models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'payment_method', 'amount', 'payment_status', 'payment_date')
    search_fields = ('order__order_number', 'transaction_id')
    list_filter = ('payment_status', 'payment_method', 'payment_date')
    readonly_fields = ('payment_date',)
