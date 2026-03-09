from django.contrib import admin
from accounts.models import User, Address


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone', 'created_at')
    search_fields = ('username', 'email', 'phone')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {'fields': ('username', 'email', 'phone')}),
        ('Profile', {'fields': ('profile_image',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'city', 'state', 'user', 'created_at')
    search_fields = ('full_name', 'city', 'street')
    list_filter = ('state', 'country', 'created_at')
    readonly_fields = ('created_at',)
