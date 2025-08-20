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

        data = json.loads(text_data)
        pixel_data = await self.save_pixel(data)  # <- now returns a dict, not a model

        await self.channel_layer.group_send(
            "pixels",
            {"type": "pixel.update", "pixel": pixel_data}
        )

    async def pixel_update(self, event):
        await self.send(text_data=json.dumps(event["pixel"]))

    async def save_pixel(self, data):
        from .models import Pixel, Player

        user = self.scope["user"]
        player, _ = await database_sync_to_async(Player.objects.get_or_create)(user=user)

        defaults = {"description": data.get("description", "")}

        def _update_and_serialize():
            # If you want to prevent other players overwriting pixels, include owner=player
            # in the filter; here we set owner in defaults (which will overwrite owner if pixel exists).
            pixel, created = Pixel.objects.update_or_create(
                x=data["x"],
                y=data["y"],
                defaults={**defaults, "owner": player}
            )

            # Make sure to access related fields (owner.user.username) while still in sync
            owner_username = None
            if pixel.owner_id:
                # pixel.owner is a Player instance; access its user.username here (sync)
                owner_username = pixel.owner.user.username

            return {
                "x": pixel.x,
                "y": pixel.y,
                "owner": owner_username or player.user.username,
                "description": pixel.description,
                "planted_on": pixel.planted_on.isoformat() if pixel.planted_on else "",
            }

        pixel_data = await database_sync_to_async(_update_and_serialize)()
        return pixel_data

