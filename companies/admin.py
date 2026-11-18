"""Admin configuration for company profiles, including the verification workflow."""

from django.contrib import admin, messages
from django.urls import reverse
from django.utils.html import format_html

from notifications.services import notify

from .models import CompanyProfile


@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    """Lets staff review companies and verify them before they can post jobs."""

    list_display = (
        'company_name', 'user', 'pan_number', 'industry', 'location',
        'is_verified', 'has_document', 'created_at',
    )
    list_filter = ('is_verified', 'industry', 'company_size')
    search_fields = ('company_name', 'pan_number', 'user__username', 'user__email')
    ordering = ('is_verified', '-created_at')   # unverified companies first
    actions = ['mark_verified', 'mark_unverified']
    readonly_fields = ('document_link',)

    @admin.display(boolean=True, description='Document')
    def has_document(self, obj):
        """Show a tick in the list when the company uploaded a registration document."""
        return bool(obj.registration_document)

    @admin.display(description='Registration document')
    def document_link(self, obj):
        """Link to the protected download view (the file has no public URL)."""
        # On the "add" page the object is not saved yet, so pk is None
        if not obj or not obj.pk:
            return "Document link will be available after saving."

        if not obj.registration_document:
            return '-'

        url = reverse('core:company_document', args=[obj.pk])
        return format_html('<a href="{}" target="_blank">View / download</a>', url)

    @admin.action(description='Mark selected companies as verified')
    def mark_verified(self, request, queryset):
        """Verify the selected companies and notify each owner."""
        count = 0
        # Only touch companies that are not verified yet, so owners are not notified twice.
        for company in queryset.filter(is_verified=False).select_related('user'):
            company.is_verified = True
            company.save(update_fields=['is_verified'])
            notify(
                company.user,
                "Your company has been verified. You can now post jobs.",
                link=reverse('jobs:create'),
                email_subject="RojGari: company verified",
            )
            count += 1
        self.message_user(request, f"{count} company verified.", messages.SUCCESS)

    @admin.action(description='Mark selected companies as unverified')
    def mark_unverified(self, request, queryset):
        """Remove verification; the company can no longer post new jobs."""
        count = queryset.filter(is_verified=True).update(is_verified=False)
        self.message_user(request, f"{count} company unverified.", messages.WARNING)