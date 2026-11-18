from django.db.models.signals import post_save
from django.dispatch import receiver

from companies.models import CompanyProfile
from jobseeker.models import JobSeekerProfile

from .models import User


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if not created:
        return
    if instance.role == 'company':
        CompanyProfile.objects.get_or_create(
            user=instance, defaults={'company_name': instance.username},
        )
    elif instance.role == 'jobseeker':
        JobSeekerProfile.objects.get_or_create(user=instance)