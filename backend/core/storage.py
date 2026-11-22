"""Database-backed originals for the small, serverless public demonstration."""

from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible


@deconstructible
class DatabaseFileStorage(Storage):
    def _open(self, name, mode="rb"):
        from core.models import PrivateDocument

        try:
            document = PrivateDocument.objects.get(pk=name)
        except PrivateDocument.DoesNotExist as exc:
            raise FileNotFoundError(name) from exc
        return ContentFile(bytes(document.content), name=name)

    def _save(self, name, content):
        from core.models import PrivateDocument

        PrivateDocument.objects.create(name=name, content=content.read())
        return name

    def exists(self, name):
        from core.models import PrivateDocument

        return PrivateDocument.objects.filter(pk=name).exists()

    def delete(self, name):
        from core.models import PrivateDocument

        PrivateDocument.objects.filter(pk=name).delete()

    def size(self, name):
        return self._open(name).size

    def url(self, name):
        raise ValueError(
            "Private documents are available only through authenticated downloads."
        )
