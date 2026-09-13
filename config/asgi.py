import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

from django.core.asgi import get_asgi_application

django_asgi_app = get_asgi_application()

from config.routing import application  # noqa: E402
