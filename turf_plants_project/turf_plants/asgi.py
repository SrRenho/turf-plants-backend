import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "turf_plants.settings")

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from game_api.routing import websocket_urlpatterns # Render toma turf_plants_project como root


application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})