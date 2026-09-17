from django.contrib import admin
from . models import Note, Images

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'content', 'updated_at')
    search_fields = ('title', 'content')
    list_filter = ('user', 'updated_at')

@admin.register(Images)
class ImagesAdmin(admin.ModelAdmin):
    list_display = ('id', 'note', 'image')
    list_filter = ('note',)