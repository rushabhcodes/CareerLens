"""Create local secrets once. Existing configuration is never overwritten."""

from pathlib import Path
import secrets

root = Path(__file__).resolve().parent.parent
target = root / ".env"
if target.exists():
    print("Existing .env retained.")
else:
    text = (root / ".env.example").read_text()
    text = text.replace("CHANGE_ME_use_a_long_random_string", secrets.token_urlsafe(48))
    text = text.replace("CHANGE_ME_application_password", secrets.token_urlsafe(24))
    text = text.replace("CHANGE_ME_root_password", secrets.token_urlsafe(24))
    target.write_text(text)
    target.chmod(0o600)
    print("Created .env with random development secrets.")
