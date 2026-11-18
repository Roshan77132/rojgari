from django.db import models
from django.conf import settings
from core.validators import (
    phone_validator, resume_validator, image_validator, validate_file_size,
)


class JobSeekerProfile(models.Model):
    EDUCATION_CHOICES = [
        ('slc', 'SLC / SEE'),
        ('plus2', '+2 / High School'),
        ('diploma', 'Diploma'),
        ('bachelor', "Bachelor's"),
        ('master', "Master's"),
    ]
    JOB_TYPE_CHOICES = [
        ('full_time', 'Full-time'),
        ('part_time', 'Part-time'),
        ('internship', 'Internship'),
        ('remote', 'Remote'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='jobseeker_profile',
    )
    photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True,
                              validators=[image_validator, validate_file_size])
    headline = models.CharField(max_length=120, blank=True)
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=16, blank=True, validators=[phone_validator])
    location = models.CharField(max_length=100, blank=True)
    education_level = models.CharField(max_length=20, choices=EDUCATION_CHOICES, blank=True)
    skills = models.CharField(max_length=300, blank=True, help_text="Comma separated: python, django")
    experience_years = models.PositiveSmallIntegerField(default=0)
    expected_salary = models.PositiveIntegerField(default=0, help_text="Monthly, NPR")
    preferred_job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, blank=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True,
                              validators=[resume_validator, validate_file_size])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

    @property
    def skills_list(self):
        return [s.strip().lower() for s in self.skills.split(',') if s.strip()]

    @property
    def completion(self):
        """How much of the profile is filled in, in percent (10 checks, 10% each)."""
        checks = [
            bool(self.photo),
            bool(self.headline),
            bool(self.bio),
            bool(self.phone),
            bool(self.location),
            bool(self.education_level),
            bool(self.skills),
            bool(self.preferred_job_type),
            bool(self.resume),
            self.expected_salary > 0,
        ]
        return round(sum(checks) * 100 / len(checks))

    def skill_list(self):
        """Skills as a clean list, e.g. 'python, django' -> ['python', 'django']."""
        return [s.strip() for s in self.skills.split(',') if s.strip()]