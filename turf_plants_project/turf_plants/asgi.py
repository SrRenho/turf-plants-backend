import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "turf_plants.settings")

# import django setup first
import django
django.setup()

# now import middleware that uses get_user_model()
from django_channels_jwt.middleware import JwtAuthMiddlewareStack
from game_api.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JwtAuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})