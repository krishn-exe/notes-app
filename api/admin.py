from django.contrib import admin
from .models import apiNotes, EmailOTP


@admin.register(apiNotes)
class ApiNotesAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'image_url', 'updated_at')
    search_fields = ('title', 'content')
    list_filter = ('user', 'updated_at')


@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'otp', 'purpose', 'is_used', 'created_at')
    search_fields = ('email', 'otp')
    list_filter = ('purpose', 'is_used', 'created_at')
