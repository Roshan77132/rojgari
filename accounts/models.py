from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
class User(AbstractUser): #(inheritance concept)
    ROLE_CHOICES = [  #( first list same as context and passing tuple)(everyoption ma label ra value hunupraxa)
        ('jobseeker', 'Job Seeker'),
        ('company', 'Company'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='jobseeker')
    email_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username