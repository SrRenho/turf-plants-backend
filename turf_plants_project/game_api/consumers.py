import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Pixel, Player

class PixelConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("pixels", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("pixels", self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        # Save pixel to DB
        pixel = await self.save_pixel(data)
        # Prepare pixel data for broadcast (include all relevant fields)
        pixel_data = {
            "x": pixel.x,
            "y": pixel.y,
            "owner__user__username": pixel.owner.user.username if pixel.owner else "Unknown",
            "description": pixel.description,
            "planted_on": pixel.planted_on.isoformat() if pixel.planted_on else "",
        }
        # Broadcast to all clients
        await self.channel_layer.group_send(
            "pixels",
            {"type": "pixel.update", "pixel": pixel_data}
        )

    async def pixel_update(self, event):
        await self.send(text_data=json.dumps(event["pixel"]))

    async def save_pixel(self, data):
        user = self.scope["user"]
        player = await database_sync_to_async(Player.objects.get)(user=user)
        # You can also handle description and other fields here
        defaults = {
            "owner": player,
            "description": data.get("description", ""),
        }
        pixel, _ = await database_sync_to_async(Pixel.objects.update_or_create)(
            x=data["x"], y=data["y"], defaults=defaults
        )
        return pixel
