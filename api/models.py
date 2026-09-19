from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class apiNotes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_notes')
    title = models.CharField(max_length=200)
    content = models.TextField()
    image_url = models.CharField(max_length=500, blank=True, default='')
    updated_at = models.DateTimeField(auto_now=True)


class EmailOTP(models.Model):
    PURPOSE_CHOICES = (
        ('registration', 'Registration'),
        ('forgot_password', 'Forgot Password'),
    )

    email = models.EmailField(db_index=True)
    otp = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_valid(self, expiration_minutes=10):
        if self.is_used:
            return False
        expiry_time = self.created_at + timedelta(minutes=expiration_minutes)
        return timezone.now() <= expiry_time

    def __str__(self):
        return f"{self.email} - {self.purpose} - {self.otp}"
