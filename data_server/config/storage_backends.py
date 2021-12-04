from tempfile import NamedTemporaryFile
from urllib.parse import urljoin

from django.conf import settings
from django.utils.deconstruct import deconstructible
from storages.backends.gcloud import GoogleCloudFile, GoogleCloudStorage
from storages.utils import clean_name, setting


class NamedGoogleCloudFile(GoogleCloudFile):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._named_file = None
    
    def get_named_file(self):
        if self._file is None:
            self._file = NamedTemporaryFile(
                suffix=".GSStorageFile",
                dir=setting("FILE_UPLOAD_TEMP_DIR"),
            )
            if 'r' in self._mode:
                self._is_dirty = False
                self.blob.download_to_file(self._file)
                self._file.seek(0)
        return self._file


class NamedGoogleCloudStorage(GoogleCloudStorage):
    def _open(self, name, mode='rb'):
        name = self._normalize_name(clean_name(name))
        file_object = NamedGoogleCloudFile(name, mode, self)
        if not file_object.blob:
            raise FileNotFoundError('File does not exist: %s' % name)
        return file_object


class GoogleCloudMediaStorage(NamedGoogleCloudStorage):
    """GoogleCloudStorage suitable for Django's Media files."""

    def __init__(self, *args, **kwargs):
        if not settings.MEDIA_URL:
            raise Exception('MEDIA_URL has not been configured')
        kwargs['bucket_name'] = setting('GS_MEDIA_BUCKET_NAME')
        super(GoogleCloudMediaStorage, self).__init__(*args, **kwargs)

    def url(self, name):
        """.url that doesn't call Google."""
        return urljoin(settings.MEDIA_URL, name)


class GoogleCloudStaticStorage(NamedGoogleCloudStorage):
    """GoogleCloudStorage suitable for Django's Static files"""

    def __init__(self, *args, **kwargs):
        if not settings.STATIC_URL:
            raise Exception('STATIC_URL has not been configured')
        kwargs['bucket_name'] = setting('GS_STATIC_BUCKET_NAME')
        super(GoogleCloudStaticStorage, self).__init__(*args, **kwargs)

    def url(self, name):
        """.url that doesn't call Google."""
        return urljoin(settings.STATIC_URL, name)
