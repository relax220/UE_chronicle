import os
from datetime import datetime
from urllib.parse import urljoin
from uuid import uuid4

from PIL import Image, ImageOps
from django.core.files.storage import FileSystemStorage
from pytils.translit import slugify

from app import settings


class CkeditorCustomStorage(FileSystemStorage):
    """
    Расположение медиа файлов редактора Ckeditor_5
    """
    @staticmethod
    def get_folder_name():
        return datetime.now().strftime('%Y/%m/%d')

    def get_valid_name(self, name):
        return name

    def _save(self, name, content):
        folder_name = self.get_folder_name()
        name = os.path.join(folder_name, self.get_valid_name(name))
        return super()._save(name, content)

    location = os.path.join(settings.MEDIA_ROOT, 'uploads/')
    base_url = urljoin(settings.MEDIA_URL, 'uploads/')


def unique_slugify(instance, slug):
    """
    Генератор уникальных SLUG для моделей, в случае существования такого SLUG.
    """
    model = instance.__class__
    unique_slug = slugify(slug)
    while model.objects.filter(slug=unique_slug).exists():
        unique_slug = f'{unique_slug}-{uuid4().hex[:8]}'
    return unique_slug


def get_client_ip(request):
    """
    IP пользователя
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
    return ip


def image_compress(image_path, height, width):
    """
    Оптимизация изображений
    """
    img = Image.open(image_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    if img.height > height or img.width > width:
        output_size = (height, width)
        img.thumbnail(output_size)
    img = ImageOps.exif_transpose(img)
    img.save(image_path, format='JPEG', quality=90, optimize=True)
