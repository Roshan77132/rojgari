from django.contrib import admin
from .models import JobSeekerProfile


@admin.register(JobSeekerProfile)
class JobSeekerProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'headline', 'phone', 'location',
        'experience_years', 'expected_salary', 'preferred_job_type', 'created_at',
    )
    list_filter = ('education_level', 'preferred_job_type', 'created_at')
    search_fields = ('user__username', 'headline', 'phone', 'location', 'skills')
    readonly_fields = ('created_at', 'updated_at')
    list_select_related = ('user',)
    list_per_page = 25