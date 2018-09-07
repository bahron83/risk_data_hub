import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import datetime

class TimestampFileStorage(FileSystemStorage):    
    def get_available_name(self, name):
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return datetime.datetime.now().strftime("%Y%m%d%H%M%S") + name

class ReplacingFileStorage(FileSystemStorage):            
    def get_available_name(self, name):
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name
    