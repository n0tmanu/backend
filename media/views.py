import re

import requests
from bs4 import BeautifulSoup
from django.http import JsonResponse, HttpResponse
from .directory_handler import DirectoryHandler
from backend import settings
from .models import File, Folder, Telegram
from .serializers import FolderSerializer, FileSerializer
from .telegram_handler import TelegramHandler

# Initialize other handlers
handler = DirectoryHandler(
        BUNNY_API_KEY=settings.BUNNY_API_KEY,
        BUNNY_STORAGE_ZONE_NAME=settings.BUNNY_STORAGE_ZONE_NAME,
        BUNNY_STORAGE_ZONE_REGION=settings.BUNNY_STORAGE_ZONE_REGION
)


classes_to_remove = [
    "js-widget_message",
    "tgme_widget_message_footer"
]
footer_link_class = "tgme_widget_message_link"
pattern = r'(?<=["\'\s])(\/\/[^"\']+\/?)(?=["\'\s])'


# Media view
def media(request):
    try:
        folder_id = request.GET.get('id')
        folder = Folder.objects.get(pk=folder_id)
        child_folders = folder.children.all()
        files = folder.files.all()

        folder_serializer = FolderSerializer(child_folders, many=True)
        file_serializer = FileSerializer(files, many=True)
        content = list(file_serializer.data) + list(folder_serializer.data)
        return JsonResponse({'content': content})

    except Folder.DoesNotExist:
        return HttpResponse("File or Folder not found", status=404)


def telegram(request):
    add_offset = request.GET.get('add_offset')
    if add_offset:
        add_offset = int(add_offset)
    else:
        add_offset = 0

    limit = 10

    objects = Telegram.objects.all().order_by('-id')[add_offset:add_offset+limit]

    message_ids = [obj.id for obj in objects]

    return JsonResponse(
        {
            'ids': message_ids,
            "offset": add_offset + 10
        },
        safe=False
    )


def database(request):
    handler.get_bunny_objects()


def edit_page_source(request):
    media_id = request.GET.get('media_id')

    content = requests.get(f"https://t.me/hweifbwifjbwjvb/{media_id}?embed=1")
    page = content.text

    page = page.replace("\n", "")
    page = page.replace("anon we cant confirm", "Nay ViP 10 🔞")

    page = re.sub(pattern, r'https:\1', page)

    soup = BeautifulSoup(page, 'html.parser')

    for class_name in classes_to_remove:
        elements = soup.find_all(class_=class_name)

        for element in elements:
            # Find all child <a> elements and remove the href attribute
            for child in element.find_all('a'):
                del child['href']

    element_to_delete = soup.find(class_=footer_link_class)

    if element_to_delete:
        element_to_delete.extract()
    else:
        print(element_to_delete)

    return str(soup)

