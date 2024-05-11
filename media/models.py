from django.db import models
import uuid
from backend import settings



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

    def get_parent_folders(self):
        # Initialize a list to store parent folder data
        parent_folders_data = []

        # Add the data of the current folder to the list
        parent_folders_data.append({
            'id': str(self.id),
            'name': self.name
        })

        # Get the parent folder of the current folder
        parent_folder = self.parent

        # Iterate through parent folders until reaching the root
        while parent_folder is not None:
            # Add the parent folder data to the list
            parent_folders_data.append({
                'id': str(parent_folder.id),
                'name': parent_folder.name
            })
            # Update the parent folder to its own parent
            parent_folder = parent_folder.parent

        # Return the list of parent folder data
        return parent_folders_data[::-1]


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
