from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone

from companies.models import CompanyProfile


class JobQuerySet(models.QuerySet):
    def open(self):
        return self.filter(
            is_active=True,
            deadline__gte=timezone.localdate(),
            company__is_verified=True,
        )


class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ('full_time', 'Full-time'),
        ('part_time', 'Part-time'),
        ('internship', 'Internship'),
        ('remote', 'Remote'),
    ]
    LEVEL_CHOICES = [
        ('entry', 'Entry level'),
        ('mid', 'Mid level'),
        ('senior', 'Senior level'),
    ]

    company = models.ForeignKey(
        CompanyProfile, on_delete=models.CASCADE, related_name='jobs',
    )
    title = models.CharField(max_length=120)
    description = models.TextField()
    requirements = models.TextField(blank=True)
    skills = models.CharField(
        max_length=300, blank=True,
        help_text="Comma separated: python, django",
    )
    location = models.CharField(max_length=100)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='entry')
    vacancies = models.PositiveSmallIntegerField(default=1)
    salary_min = models.PositiveIntegerField(null=True, blank=True, help_text="Monthly, NPR")
    salary_max = models.PositiveIntegerField(null=True, blank=True, help_text="Monthly, NPR")
    deadline = models.DateField()
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = JobQuerySet.as_manager()

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active', 'deadline']),
        ]

    def __str__(self):
        return f"{self.title} - {self.company.company_name}"

    def get_absolute_url(self):
        return reverse('jobs:detail', args=[self.pk])

    @property
    def is_open(self):
        return self.is_active and self.deadline >= timezone.localdate()

    @property
    def skills_list(self):
        return [s.strip() for s in self.skills.split(',') if s.strip()]

    @property
    def salary_display(self):
        if self.salary_min and self.salary_max:
            return f"NPR {self.salary_min:,} - {self.salary_max:,}"
        if self.salary_min:
            return f"NPR {self.salary_min:,}+"
        if self.salary_max:
            return f"Up to NPR {self.salary_max:,}"
        return "Negotiable"


class SavedJob(models.Model):
    """Jobseeker le save gareko job."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_jobs',
    )
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='saved_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['user', 'job'], name='unique_saved_job'),
        ]

    def __str__(self):
        return f"{self.user} saved {self.job}"