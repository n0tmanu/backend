import re
import requests
from bs4 import BeautifulSoup
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .directory_handler import DirectoryHandler, classify_file
from backend import settings
from .models import Folder, Telegram, File
from .serializers import FolderSerializer, FileSerializer
from .telegram_handler import TelegramHandler
import random
from django.core.paginator import EmptyPage
from django.db.models import Q


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
    most_viewed = None

    try:
        folder_id = request.GET.get('id')
        context = request.GET.get('context')

        if folder_id == 'search':
            term = context
            result_folders = Folder.objects.filter(name__icontains=term)
            result_files = File.objects.filter(name__icontains=term)

            files = FileSerializer(result_files, many=True)
            folders = FolderSerializer(result_folders, many=True)

            data = list(folders.data) + list(files.data)

            next_context = None

            bread_crumbs = [{
                "id": "be43dfef-7840-44cf-92f9-151b418c2e1c",
                "name": "media"
            }]

        else:

            if not context:
                context = 0  # Default starting point
            else:
                context = int(context)

            folder = Folder.objects.get(pk=folder_id)
            child_folders = folder.children.all()
            print(len(child_folders))
            files = folder.files.all()

            file_serializer = FileSerializer(files, many=True)

            paginator = Paginator(folder.children.all(), settings.FOLDER_CONTENT_AMOUNT, allow_empty_first_page=True)  # Set the page size to 100

            bread_crumbs = folder.get_parent_folders()

            try:
                folders_page = paginator.page(context // settings.FOLDER_CONTENT_AMOUNT + 1)  # Calculate the page number
                data = list(FolderSerializer(folders_page.object_list, many=True).data) + list(file_serializer.data)
                next_context = context + 100 if folders_page.has_next() else None
            except EmptyPage:
                return HttpResponse("EndOfFolder", status=404)
            print(next_context)

        return JsonResponse({
            'content': data,
            'next_context': next_context,
            'bread_crumbs': bread_crumbs
        })

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
    name = request.GET.get("name")
    path = request.GET.get("path")
    media_url = f"https://silly-media-pull-zone.b-cdn.net/{path}/{name}"
    thumb_url = f"https://silly-thumb.b-cdn.net/{path}/{name}.png"
    file_type = classify_file(name)

    folders = path.split("/")
    
    parent = Folder.objects.get(id=settings.HOME_FOLDER_KEY)

    for folder in folders:
        folder, created = Folder.objects.get_or_create(name=folder, parent=parent)
        parent = folder
        

    file, created = File.objects.get_or_create(
            name=name,
            folder=parent,
            url=media_url,
            thumb=thumb_url,
            type=file_type
            )    
    
    print(file)
    return JsonResponse({"status": created, "file": file.name})

async def update_telegram(request):
    # Update Telegram messages asynchronously
    telegram_handler = TelegramHandler()
    message_count = await telegram_handler.get_messages()
    return JsonResponse({"count": message_count}, safe=False)


def have_mutual_elements(class1, class2):
    # Check if two sets or lists have mutual elements
    return bool(set(class1) & set(class2))
