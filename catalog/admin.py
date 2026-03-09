from django.contrib import admin
from catalog.models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'description')
    search_fields = ('category_name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'category', 'price', 'stock', 'is_active', 'created_at')
    search_fields = ('name', 'author', 'description')
    list_filter = ('category', 'is_active', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Product Information', {'fields': ('name', 'author', 'category', 'description')}),
        ('Pricing & Stock', {'fields': ('price', 'stock')}),
        ('Media', {'fields': ('image',)}),
        ('Status', {'fields': ('is_active',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
