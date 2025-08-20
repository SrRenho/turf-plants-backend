import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class PixelConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("pixels", self.channel_name)
        await self.accept()

    async def receive(self, text_data):
        user = self.scope["user"]

        if not user.is_authenticated:
            await self.send(text_data=json.dumps({"error": "Authenticate first"}))
            return

        data = json.loads(text_data)  # contains only x, y
        pixel = await self.save_pixel(data)  # save pixel

        pixel_data = {
            "x": pixel.x,
            "y": pixel.y,
            "owner": pixel.owner.user.username if pixel.owner else "Unknown",
            "description": pixel.description,
            "planted_on": pixel.planted_on.isoformat() if pixel.planted_on else "",
        }

        await self.channel_layer.group_send(
            "pixels",
            {"type": "pixel.update", "pixel": pixel_data}
        )

    async def pixel_update(self, event):
        await self.send(text_data=json.dumps(event["pixel"]))

    async def save_pixel(self, data):
        from .models import Pixel, Player

        user = self.scope["user"]


        real_user = user._wrapped if hasattr(user, "_wrapped") else user
        player, _ = await database_sync_to_async(Player.objects.get_or_create)(user=real_user)

        defaults = {"owner": player}

        # Only set description if present, otherwise leave blank
        if "description" in data:
            defaults["description"] = data["description"]

        def _update_or_create():
            return Pixel.objects.update_or_create(
                x=data["x"], y=data["y"], defaults=defaults
            )

        pixel, _ = await database_sync_to_async(_update_or_create)()
        return pixel

