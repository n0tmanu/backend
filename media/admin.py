from django.contrib import admin
from .models import Folder, File


class FolderAdmin(admin.ModelAdmin):
    search_fields = ['id', 'name']  # Add fields you want to search here


admin.site.register(Folder)
admin.site.register(File)
