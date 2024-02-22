from rest_framework import serializers
from .models import Folder, File


class FolderSerializer(serializers.ModelSerializer):
    isDir = serializers.BooleanField(default=True)

    class Meta:
        model = Folder
        fields = ('id', 'name', 'isDir')


class FileSerializer(serializers.ModelSerializer):
    isDir = serializers.BooleanField(default=False)

    class Meta:
        model = File
        fields = ('id', 'name', 'type', 'url', 'thumb', 'isDir')

