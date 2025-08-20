import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "turf_plants.settings")

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from game_api.routing import websocket_urlpatterns
from django_channels_jwt.middleware import JwtAuthMiddlewareStack


application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JwtAuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
    ),
})
