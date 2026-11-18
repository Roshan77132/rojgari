from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import JobSeekerProfile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_jobseeker_profile(sender, instance, created, **kwargs):
    if created and instance.role == 'jobseeker' and not instance.is_superuser:
        JobSeekerProfile.objects.get_or_create(user=instance)