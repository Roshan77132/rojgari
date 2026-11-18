from django.db import models
from django.conf import settings
from core.validators import (
    phone_validator, pan_validator, image_validator,
    resume_validator, validate_file_size,
)


class CompanyProfile(models.Model):
    INDUSTRY_CHOICES = [
        ('it', 'IT & Software'),
        ('banking', 'Banking & Finance'),
        ('education', 'Education'),
        ('health', 'Healthcare'),
        ('manufacturing', 'Manufacturing'),
        ('tourism', 'Tourism & Hospitality'),
        ('ngo', 'NGO / INGO'),
        ('retail', 'Retail & Trade'),
        
        ('other', 'Other'),
    ]
    SIZE_CHOICES = [
        ('1-10', '1-10 employees'),
        ('11-50', '11-50 employees'),
        ('51-200', '51-200 employees'),
        ('201-500', '201-500 employees'),
        ('500+', '500+ employees'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='company_profile',
    )
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True,
                             validators=[image_validator, validate_file_size])
    company_name = models.CharField(max_length=150)
    tagline = models.CharField(max_length=150, blank=True)
    description = models.TextField(blank=True)

    industry = models.CharField(max_length=20, choices=INDUSTRY_CHOICES, blank=True)
    company_size = models.CharField(max_length=10, choices=SIZE_CHOICES, blank=True)
    established_year = models.PositiveSmallIntegerField(null=True, blank=True)

    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=16, blank=True, validators=[phone_validator])

    pan_number = models.CharField(max_length=9, blank=True, validators=[pan_validator])
    registration_document = models.FileField(
        upload_to='company_docs/', blank=True, null=True,
        validators=[resume_validator, validate_file_size],
    )
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name