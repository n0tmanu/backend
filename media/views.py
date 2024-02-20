from django.http import JsonResponse, HttpResponse
from .directory_handler import DirectoryHandler
from backend import settings
from .cache_handler import CacheHandler
from datetime import datetime
from .models import File, Folder
from .serializers import FolderSerializer, FileSerializer


handler = DirectoryHandler(
    AWS_ACCESS_KEY_ID=settings.AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY=settings.AWS_SECRET_ACCESS_KEY,
    AWS_REGION=settings.AWS_S3_REGION_NAME,
    AWS_BUCKET=settings.AWS_BUCKET,
    AWS_THUMB_BUCKET=settings.THUMB_BUCKET
)

cache_handler = CacheHandler(settings.cache_expire)
cache_handler.set_time(datetime.now())


def media(request):
    try:
        folder = Folder.objects.get(pk=request.GET.get('id'))
        child_folders = folder.children.all()
        files = folder.files.all()

        folder_serializer = FolderSerializer(child_folders, many=True)
        file_serializer = FileSerializer(files, many=True)
    except Folder.DoesNotExist:
        return HttpResponse("File or Folder not found", status=404)
    print(folder)
    return JsonResponse({
        'content': file_serializer.data + folder_serializer.data,
    })

