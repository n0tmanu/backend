from django.db import models
import uuid


class Folder(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    def __str__(self):
        return self.name


class File(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='files')
    type = models.CharField(max_length=255)
    url = models.CharField(max_length=255)

    def __str__(self):
        return self.name
