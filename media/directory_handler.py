import boto3
from .models import File, Folder
import os
import re


class DirectoryHandler:
    def __init__(self,
                 AWS_ACCESS_KEY_ID: str,
                 AWS_SECRET_ACCESS_KEY: str,
                 AWS_REGION: str,
                 AWS_BUCKET: str,
                 AWS_THUMB_BUCKET: str
                 ):
        self.AWS_ACCESS_KEY_ID = AWS_ACCESS_KEY_ID
        self.AWS_SECRET_ACCESS_KEY = AWS_SECRET_ACCESS_KEY
        self.AWS_REGION = AWS_REGION
        self.AWS_BUCKET = AWS_BUCKET
        self.AWS_THUMB_BUCKET = AWS_THUMB_BUCKET
        self.fetching = False

        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=self.AWS_SECRET_ACCESS_KEY,
            region_name=self.AWS_REGION
        )

    def get_s3_folder_tree(self, prefix='media/'):
        paginator = self.s3_client.get_paginator('list_objects_v2')
        page_iterator = paginator.paginate(Bucket=self.AWS_BUCKET, Prefix=prefix)

        print("Fetching Folders from S3")

        for page in page_iterator:
            for obj in page['Contents']:
                key = obj["Key"]
                key_parts = key.split('/')
                # Iterate through each part of the key to create folders and files
                current_parent = None
                for i, part in enumerate(key_parts):
                    if i == len(key_parts) - 1:  # Last part is a file
                        key = obj["Key"]
                        if not classify_file(key):
                            continue
                        else:
                            file_type = classify_file(key)
                        if not obj["Key"][0] == "/":
                            key = "/" + key
                        File.objects.create(
                            name=part,
                            folder=current_parent,
                            url=f"https://sillymediabucket.s3.eu-north-1.amazonaws.com{key}",
                            thumb=f"https://sillythumbs.s3.eu-north-1.amazonaws.com{key}.png",
                            type=file_type
                        )
                    else:  # Parts before the last are folders
                        folder, created = Folder.objects.get_or_create(name=part, parent=current_parent)
                        current_parent = folder
        print("Fetched folders and files from S3")



    def create_tree(self, object_keys):
        def generate_id():
            generate_id.counter += 1
            return str(generate_id.counter)

        generate_id.counter = 0

        # Initialize an empty dictionary to store the tree structure
        tree = {
            'id': 'root',
            'name': 'Folders',
            'children': []
        }

        # Helper function to add nodes to the tree
        def add_node(tree, path):
            parts = path.split('/')
            current = tree
            for part in parts[1:]:  # Skip the root node
                if part not in [child['name'] for child in current['children']]:
                    child_id = generate_id()
                    child = {'id': child_id, 'name': part, 'children': []}
                    current['children'].append(child)
                else:
                    child = next(c for c in current['children'] if c['name'] == part)
                current = child

        # Add each object key to the tree
        for key in object_keys:
            add_node(tree, key)

        return tree

    def set_fetching_status(self, status: bool):
        self.fetching = status


def classify_file(file_path):
    filename, extension = os.path.splitext(file_path)
    ext = extension.lower()

    if re.match(r'\.(jpg|jpeg|png|gif|bmp)$', ext):
        return "image"
    elif re.match(r'\.(mp4|avi|mov|mkv|wmv)$', ext):
        return "video"
    else:
        return False


def get_folder(key: str):
    parts = key.split('/')
    parts.pop()
    path_without_filename = '/'.join(parts)
    if path_without_filename.endswith('/'):
        path_without_filename = path_without_filename[:-1]

    return path_without_filename

