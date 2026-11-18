from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Admin panel ko table ma dekhine column haru
    list_display = ('username', 'email', 'role', 'email_verified',
                    'is_active', 'is_staff', 'date_joined')

    # Right side ko filter box
    list_filter = ('role', 'email_verified', 'is_active', 'is_staff', 'is_superuser')

    # Mathi ko search box
    search_fields = ('username', 'email')
    ordering = ('-date_joined',)

    # Tick garera chalaune action haru
    actions = ['mark_email_verified', 'deactivate_users', 'activate_users']

    # User edit garne page ma role ra email_verified dekhauna
    fieldsets = UserAdmin.fieldsets + (
        ('RojGari', {'fields': ('role', 'email_verified')}),
    )

    # Admin bata naya user banaunda
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('RojGari', {'fields': ('email', 'role', 'email_verified')}),
    )

    @admin.action(description='Mark selected users as email verified')
    def mark_email_verified(self, request, queryset):
        n = queryset.update(email_verified=True)
        self.message_user(request, f'{n} user(s) verified.')

    @admin.action(description='Deactivate selected users')
    def deactivate_users(self, request, queryset):
        n = queryset.exclude(pk=request.user.pk).update(is_active=False)
        self.message_user(request, f'{n} user(s) deactivated.')

    @admin.action(description='Activate selected users')
    def activate_users(self, request, queryset):
        n = queryset.update(is_active=True)
        self.message_user(request, f'{n} user(s) activated.')