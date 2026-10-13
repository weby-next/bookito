from .base import *

DEBUG = False

# حتماً از env بخوان
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")
if ALLOWED_HOSTS == [""]:
    ALLOWED_HOSTS = []

# امنیت کوکی/HTTPS
SECURE_SSL_REDIRECT = os.environ.get("DJANGO_SECURE_SSL_REDIRECT", "1") == "1"
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# هدرهای امنیتی
SECURE_HSTS_SECONDS = int(os.environ.get("DJANGO_SECURE_HSTS_SECONDS", "31536000"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# در پروداکشن معمولاً DB باید postgres باشد و از env پر شود (base همین کار را می‌کند)
# مطمئن شو DB_ENGINE/DB_NAME/... را ست می‌کنی