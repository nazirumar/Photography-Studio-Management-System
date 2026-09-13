from channels.routing import ProtocolTypeRouter, URLRouter

from apps.notifications.routing import websocket_urlpatterns as notification_ws
from apps.portal.routing import websocket_urlpatterns as portal_ws

from django.core.asgi import get_asgi_application

django_asgi_app = get_asgi_application()

all_ws_patterns = notification_ws + portal_ws

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": URLRouter(all_ws_patterns),
})
