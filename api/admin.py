from django.contrib import admin
from .models import apiNotes


@admin.register(apiNotes)
class ApiNotesAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'image_url', 'updated_at')
    search_fields = ('title', 'content')
    list_filter = ('user', 'updated_at')
