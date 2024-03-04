from rest_framework import serializers
from .models import Folder, File


class FolderSerializer(serializers.ModelSerializer):
    # Serializer for Folder model
    isDir = serializers.BooleanField(default=True)  # Custom field for indicating it's a directory

    class Meta:
        model = Folder
        fields = ('id', 'name', 'isDir')  # Fields to include in the serialized output


class FileSerializer(serializers.ModelSerializer):
    # Serializer for File model
    isDir = serializers.BooleanField(default=False)  # Custom field for indicating it's a file

    class Meta:
        model = File
        fields = ('id', 'name', 'type', 'url', 'thumb', 'isDir')  # Fields to include in the serialized output
