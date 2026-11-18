from django.contrib import admin
from .models import Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'job_type', 'location', 'deadline', 'is_active')
    list_filter = ('job_type', 'level', 'is_active')
    search_fields = ('title', 'company__company_name', 'location')