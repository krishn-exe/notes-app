from django.db import models
from django.contrib.auth.models import User

class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_notes')
    title = models.CharField(max_length=200)
    content = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)

class Images(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='images')
    image_url = models.CharField(max_length=500)