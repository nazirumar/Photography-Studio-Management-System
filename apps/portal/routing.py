from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/portal/$", consumers.ClientPortalConsumer.as_asgi()),
]
