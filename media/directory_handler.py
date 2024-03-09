from BunnyCDN.Storage import Storage
from .models import File, Folder
import os
import re
import cv2
from urllib.parse import quote
from PIL import Image


class DirectoryHandler:
    def __init__(
            self,
            BUNNY_MEDIA_API_KEY: str,
            BUNNY_THUMB_API_KEY: str,
            BUNNY_STORAGE_ZONE_NAME: str,
            BUNNY_STORAGE_THUMB_ZONE_NAME: str,
            BUNNY_STORAGE_ZONE_REGION: str):
        """
        Initializes the DirectoryHandler with Bunny CDN credentials.
        """
        self.obj_storage = Storage(
            BUNNY_MEDIA_API_KEY,
            BUNNY_STORAGE_ZONE_NAME,
            BUNNY_STORAGE_ZONE_REGION
        )

        self.thumb_storage = Storage(
            BUNNY_THUMB_API_KEY,
            BUNNY_STORAGE_THUMB_ZONE_NAME,
            BUNNY_STORAGE_ZONE_REGION
        )



    def get_bunny_objects(self):
        """
        Fetches folders and files from Bunny CDN and saves them to the database.
        """
        print("Fetching Folders from Bunny CDN")
        objects = self.obj_storage.GetStoragedObjectsList()
        # Get or create the root folder
        folder, created = Folder.objects.get_or_create(name="media", parent=None)
        # Save Bunny CDN objects recursively
        self.save_bunny_objects(objects, "", folder)

    def save_bunny_objects(self, storage_objects, path, parent):
        """
        Recursively saves Bunny CDN objects to the database.
        """
        if not path:
            thumb_path = None
        else:
            thumb_path = path
        thumb_objects = self.thumb_storage.GetStoragedObjectsList(thumb_path)

        for obj in storage_objects:
            if 'File_Name' in obj:
                # Process file objects
                file_name = obj['File_Name']
                file_type = classify_file(file_name)
                if not file_type:
                    continue
                if path and not path[0] == "/":
                    path = f"/{path}"
                url = f"https://silly-media-pull-zone.b-cdn.net{path}/{file_name}"
                thumb = f"https://silly-thumb.b-cdn.net{path}/{file_name}.png"
                # Create or update file object
                self.check_thumbnail(file_name, path, thumb_objects)
                File.objects.get_or_create(
                    name=file_name,
                    folder=parent,
                    url=url,
                    thumb=thumb,
                    type=file_type
                )
            elif 'Folder_Name' in obj:
                # Process folder objects
                folder_name = obj['Folder_Name']
                # Get or create folder in the database
                folder, created = Folder.objects.get_or_create(name=folder_name, parent=parent)
                # Get objects inside the folder
                objects = self.obj_storage.GetStoragedObjectsList(f"{path}/{folder_name}")
                # Recursively save objects inside the folder
                self.save_bunny_objects(storage_objects=objects, path=f"{path}/{folder_name}", parent=folder)
        print("Fetched folders and files from Bunny CDN")
        # Return count of folders and files saved in the database
        return {
            "folders": Folder.objects.all().count(),
            "files": File.objects.all().count()
        }

    def check_thumbnail(self, file, path, thumb_objects):

        if path:
            storage_path = f"{path}/{file}"
        else:
            path = None
            storage_path = file

        if thumb_objects:
            for obj in thumb_objects:
                if "File_Name" in obj and obj['File_Name'] == f"{file}.png":
                    return True

        print(self.obj_storage.DownloadFile(storage_path=storage_path)["msg"])

        file_type = classify_file(file)
        if file_type == "video":
            status = extract_first_frame(video_path=file, output_path=f"{file}.png")
        elif file_type == "image":
            status = resize_image(input_path=file, output_path=f"{file}.png")
        else:
            os.remove(file)
            return False

        if status:
            rp = self.thumb_storage.PutFile(storage_path=f"{storage_path}.png", file_name=f"{file}.png")
            print(rp['status'], f"{file}.png")

        try:
            os.remove(f"{file}.png")
        except:
            pass


def classify_file(file_path):
    """
    Classifies the file based on its extension.
    """
    filename, extension = os.path.splitext(file_path)
    ext = extension.lower()
    if re.match(r'\.(jpg|jpeg|png|gif|bmp)$', ext):
        return "image"
    elif re.match(r'\.(mp4|avi|mov|mkv|wmv)$', ext):
        return "video"
    else:
        return False


def extract_first_frame(video_path, output_path):

    if not os.path.exists(video_path):
        video_path = quote(video_path)
    # Open the video file
    video_capture = cv2.VideoCapture(video_path)

    # Check if the video file is opened successfully
    if not video_capture.isOpened():
        video_capture = cv2.VideoCapture(video_path)

        print("Error: Unable to open video file.")
        return False

    # Read the first frame
    success, frame = video_capture.read()

    # Check if the frame is read successfully
    if not success:
        print("Error: Unable to read the first frame.")
        return False

    frame = cv2.resize(frame, (320, 240))

    # Save the first frame as an image file
    cv2.imwrite(output_path, frame)

    # Release the video capture object
    video_capture.release()
    os.remove(video_path)

    return True


def resize_image(input_path, output_path):
    if not os.path.exists(input_path):
        input_path = quote(input_path)

    try:
        # Open the image file
        image = Image.open(input_path)

        # Resize the image
        resized_image = image.resize((320, 240))

        # Save the resized image
        resized_image.save(output_path)

        print("Image resized successfully.")
        try:
            os.remove(input_path)
        except:
            pass
        return True

    except Exception as e:
        print(f"Error resizing image: {str(e)}")
        return False
