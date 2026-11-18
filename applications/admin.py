from django.contrib import admin

from .models import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'job', 'company_name', 'status', 'applied_at')
    list_filter = ('status', 'applied_at')
    search_fields = (
        'applicant__user__username', 'applicant__user__email',
        'job__title', 'job__company__company_name',
    )
    list_select_related = ('applicant__user', 'job__company')
    list_per_page = 25
    date_hierarchy = 'applied_at'
    readonly_fields = ('applied_at', 'updated_at')

    @admin.display(description='Company', ordering='job__company__company_name')
    def company_name(self, obj):
        return obj.job.company.company_name