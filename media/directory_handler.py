import requests
from BunnyCDN.Storage import Storage
from bs4 import BeautifulSoup

from .models import File, Folder
import os
import re


class DirectoryHandler:
    def __init__(self,
                 BUNNY_API_KEY: str,
                 BUNNY_STORAGE_ZONE_NAME: str,
                 BUNNY_STORAGE_ZONE_REGION: str,
                 ):

        self.obj_storage = Storage(BUNNY_API_KEY,BUNNY_STORAGE_ZONE_NAME,BUNNY_STORAGE_ZONE_REGION)

    def get_bunny_objects(self):
        print("Fetching Folders from Bunny CDN")
        objects = self.obj_storage.GetStoragedObjectsList()
        folder, created = Folder.objects.get_or_create(name="media", parent=None)
        self.save_bunny_objects(objects, "", folder)

    def save_bunny_objects(self, storage_objects, path, parent):
        print(path)
        for obj in storage_objects:
            if 'File_Name' in obj:
                file_name = obj['File_Name']
                file_type = classify_file(file_name)

                if not file_type:
                    continue

                if path and not path[0] == "/":
                    path = f"/{path}"

                url = f"https://silly-media-pull-zone.b-cdn.net{path}/{file_name}"
                thumb = f"https://silly-thumb.b-cdn.net{path}/{file_name}.png"

                File.objects.get_or_create(
                    name=file_name,
                    folder=parent,
                    url=url,
                    thumb=thumb,
                    type=file_type
                )

            elif 'Folder_Name' in obj:
                folder_name = obj['Folder_Name']
                folder, created = Folder.objects.get_or_create(name=folder_name, parent=parent)

                objects = self.obj_storage.GetStoragedObjectsList(f"{path}/{folder_name}")
                self.save_bunny_objects(storage_objects=objects, path=f"{path}/{folder_name}", parent=folder)

        print("Fetched folders and files from Bunny CDN")
        return {
            "folders": Folder.objects.all().count(),
            "files": File.objects.all().count()
        }



def classify_file(file_path):
    filename, extension = os.path.splitext(file_path)
    ext = extension.lower()

    if re.match(r'\.(jpg|jpeg|png|gif|bmp)$', ext):
        return "image"
    elif re.match(r'\.(mp4|avi|mov|mkv|wmv)$', ext):
        return "video"
    else:
        return False


