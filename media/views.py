import re
import requests
from bs4 import BeautifulSoup
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .directory_handler import DirectoryHandler
from backend import settings
from .models import Folder, Telegram
from .serializers import FolderSerializer, FileSerializer
from .telegram_handler import TelegramHandler

# Initialize the DirectoryHandler
handler = DirectoryHandler(
    BUNNY_MEDIA_API_KEY=settings.BUNNY_MEDIA_API_KEY,
    BUNNY_THUMB_API_KEY=settings.BUNNY_THUMB_API_KEY,
    BUNNY_STORAGE_ZONE_NAME=settings.BUNNY_STORAGE_ZONE_NAME,
    BUNNY_STORAGE_THUMB_ZONE_NAME=settings.BUNNY_STORAGE_THUMB_ZONE_NAME,
    BUNNY_STORAGE_ZONE_REGION=settings.BUNNY_STORAGE_ZONE_REGION
)

# Constants and patterns
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

        # Serialize folders and files
        folder_serializer = FolderSerializer(child_folders, many=True)
        file_serializer = FileSerializer(files, many=True)
        content = list(file_serializer.data) + list(folder_serializer.data)
        return JsonResponse({'content': content})
    except Folder.DoesNotExist:
        return HttpResponse("File or Folder not found", status=404)


def telegram(request):
    # Retrieve message IDs with pagination
    add_offset = int(request.GET.get('add_offset', 0))
    limit = 5
    objects = Telegram.objects.all().order_by('-id')[add_offset:add_offset + limit]
    message_ids = [obj.id for obj in objects]
    return JsonResponse({'ids': message_ids, "offset": add_offset + 5}, safe=False)


@csrf_exempt
def edit_page_source(request):
    media_id = request.GET.get('media_id')
    # Fetch content from a URL and process it
    content = requests.get(f"https://t.me/hweifbwifjbwjvb/{media_id}?embed=1").text
    # Manipulate HTML content
    content = content.replace("\n", "").replace("anon we cant confirm", "Nay ViP 10 🔞")
    content = re.sub(pattern, r'https:\1', content)
    soup = BeautifulSoup(content, 'html.parser')
    # Remove specified classes and elements
    for class_name in classes_to_remove:
        elements = soup.find_all(class_=class_name)
        for element in elements:
            for child in element.find_all('a'):
                del child['href']
    element_to_delete = soup.find(class_=footer_link_class)
    if element_to_delete:
        element_to_delete.extract()
    # Inject JavaScript into the HTML
    script_tag = soup.new_tag("script")
    script_tag.string = """
        function sendHeightToParent() {
            const element = document.querySelector('.tgme_widget_message');
            if (element) {
                const elementHeight = element.scrollHeight;
                window.parent.postMessage({ type: 'message', height: elementHeight }, '*');
            }
        }

        window.addEventListener('resize', sendHeightToParent);
        sendHeightToParent();
    """
    soup.body.append(script_tag)
    response = HttpResponse(str(soup))
    response['X-Frame-Options'] = 'ALLOWALL'
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response['Access-Control-Allow-Headers'] = 'Origin, Content-Type, Accept'
    return response


def update_database(request):
    # Update database with files and folders from Bunny CDN
    count = handler.get_bunny_objects()
    return JsonResponse(count, safe=False)


async def update_telegram(request):
    # Update Telegram messages asynchronously
    telegram_handler = TelegramHandler()
    message_count = await telegram_handler.get_messages()
    return JsonResponse({"count": message_count}, safe=False)


def have_mutual_elements(class1, class2):
    # Check if two sets or lists have mutual elements
    return bool(set(class1) & set(class2))
