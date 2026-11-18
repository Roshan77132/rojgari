from django.db import models

# Create your models here.

from core.validators import resume_validator, validate_file_size
from jobs.models import Job
from jobseeker.models import JobSeekerProfile


class Application(models.Model):
    class Status(models.TextChoices):
        APPLIED = 'applied', 'Applied'
        SHORTLISTED = 'shortlisted', 'Shortlisted'
        REJECTED = 'rejected', 'Rejected'
        HIRED = 'hired', 'Hired'

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(
        JobSeekerProfile, on_delete=models.CASCADE, related_name='applications',
    )
    cover_letter = models.TextField(blank=True)
    resume = models.FileField(
        upload_to='application_resumes/',
        validators=[resume_validator, validate_file_size],
    )
    status = models.CharField(
        max_length=12, choices=Status.choices, default=Status.APPLIED,
    )
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-applied_at']
        constraints = [
            models.UniqueConstraint(
                fields=['job', 'applicant'], name='unique_application_per_job',
            ),
        ]
        indexes = [models.Index(fields=['job', 'status'])]

    def __str__(self):
        return f"{self.applicant} -> {self.job.title}"