from django.db import models
from django.contrib.auth.models import User

class apiNotes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_notes')
    title = models.CharField(max_length=200)
    content = models.TextField()
    image_url = models.CharField(max_length=500, blank=True, default='')
    updated_at = models.DateTimeField(auto_now=True)
