import os
from datetime import datetime
from urllib.parse import urljoin

from django.core.files.storage import FileSystemStorage

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
