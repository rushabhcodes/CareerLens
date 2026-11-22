"""Create a demonstration administrator with a random password, never print it."""

from pathlib import Path
import os
import sys
import secrets

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root / "backend"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django

django.setup()
from django.contrib.auth import get_user_model
from core.models import Profile

email = "admin@careerlens.local"
if get_user_model().objects.filter(email=email).exists():
    print("Local administrator already exists. Credentials were not changed.")
else:
    password = secrets.token_urlsafe(18)
    user = get_user_model().objects.create_superuser(
        username="careerlens-admin",
        email=email,
        password=password,
        first_name="Local",
        last_name="Administrator",
    )
    Profile.objects.create(user=user, headline="Local demonstration administrator")
    directory = root / ".runtime"
    directory.mkdir(mode=0o700, exist_ok=True)
    directory.chmod(0o700)
    target = directory / "admin-credentials.txt"
    target.write_text(
        f"Frontend email: {email}\nDjango admin username: careerlens-admin\nPassword: {password}\n"
    )
    target.chmod(0o600)
    print(
        "Created a local administrator. Read .runtime/admin-credentials.txt privately to sign in."
    )
