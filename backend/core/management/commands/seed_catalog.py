from django.core.management.base import BaseCommand
from core.services.catalog import seed_catalog


class Command(BaseCommand):
    help = "Install the skill, career role and official learning resource catalog (no user data)."

    def handle(self, *args, **kwargs):
        seed_catalog()
        self.stdout.write(self.style.SUCCESS("Career catalog is ready."))
