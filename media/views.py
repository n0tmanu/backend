import re

import requests
from bs4 import BeautifulSoup
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

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

    limit = 5

    objects = Telegram.objects.all().order_by('-id')[add_offset:add_offset+limit]

    message_ids = [obj.id for obj in objects]

    return JsonResponse(
        {
            'ids': message_ids,
            "offset": add_offset + 5
        },
        safe=False
    )


def database(request):
    count = handler.get_bunny_objects()
    return JsonResponse(
        count, safe=False
    )


@csrf_exempt
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

    script_tag = soup.new_tag("script")
    script_tag.string = """
        function sendHeightToParent() {
            const element = document.querySelector('.tgme_widget_message');
            if (element) {
                const elementHeight = element.scrollHeight;
                window.parent.postMessage({ type: 'message', height: elementHeight }, '*');
            }
        }


        // Listen for changes in the iframe's content height
        window.addEventListener('resize', sendHeightToParent);

        // Initial call to send the document height
        sendHeightToParent();
    """

    soup.body.append(script_tag)

    response = HttpResponse(str(soup))

    # Set the X-Frame-Options header to allow embedding in iframes from any origin
    response['X-Frame-Options'] = 'ALLOWALL'

    # Set CORS headers to allow cross-origin requests
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response['Access-Control-Allow-Headers'] = 'Origin, Content-Type, Accept'

    return response


def have_mutual_elements(class1, class2):
    # Assuming class1 and class2 are lists or sets of elements
    set1 = set(class1)
    set2 = set(class2)

    # Check if there is any common element between set1 and set2
    common_elements = set1.intersection(set2)

    # If the length of the common elements set is greater than 0, they have mutual elements
    if len(common_elements) > 0:
        return True
    else:
        return False