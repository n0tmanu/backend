from django.db import models
import uuid


class Folder(models.Model):
    # Unique identifier for the folder
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Name of the folder
    name = models.CharField(max_length=255)
    # Parent folder (self-referencing relationship)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    def __str__(self):
        # String representation of the folder
        return self.name


class File(models.Model):
    # Unique identifier for the file
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Name of the file
    name = models.CharField(max_length=255)
    # Folder the file belongs to (many-to-one relationship with Folder model)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='files')
    # Type of the file (e.g., image, video, etc.)
    type = models.CharField(max_length=255)
    # URL of the file
    url = models.CharField(max_length=255)
    # URL of the file's thumbnail
    thumb = models.CharField(max_length=255)

    def __str__(self):
        # String representation of the file
        return self.name


class Telegram(models.Model):
    # Primary key representing the Telegram message ID
    id = models.IntegerField(primary_key=True)

    # Additional fields and methods can be added as needed
