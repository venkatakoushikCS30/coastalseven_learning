from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('DOCTOR', 'Doctor'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='DOCTOR')
    email = models.EmailField(unique=True)
    specialization = models.CharField(max_length=100, blank=True, default='')
    study = models.CharField(max_length=100, blank=True, default='')
    available_hours = models.CharField(max_length=100, blank=True, default='')

    # Use email for login or username, let's keep username for simplicity but ensure email is unique
    def __str__(self):
        return f"{self.username} ({self.role})"
