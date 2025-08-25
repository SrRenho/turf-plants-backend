import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from game_api.level_system import xp_progress

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
        pixel_data = await self.save_pixel(data)

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

        if player.seeds < 1:
            # Return an error instead of saving
            return {"error": "Not enough seeds"}

        defaults = {"description": data['description']}

        def _update_and_serialize():
            pixel, created = Pixel.objects.update_or_create(
                x=data["x"],
                y=data["y"],
                defaults={**defaults, "owner": player}
            )

            # Only deduct a seed if a new pixel was created
            if created:
                player.seeds -= 1
                player.save()

            owner_username = pixel.owner.user.username if pixel.owner_id else player.user.username
            level, xp_into_level, xp_until_next = xp_progress(pixel.total_xp)
            return {"x": pixel.x,
                    "y": pixel.y,
                    "owner": owner_username,
                    "description": pixel.description,
                    "planted_on": pixel.planted_on.isoformat() if pixel.planted_on else "",
                    "total_xp": pixel.total_xp,
                    "level": level,
                    "xp_into_level": xp_into_level,
                    "xp_until_next": xp_until_next, }



        pixel_data = await database_sync_to_async(_update_and_serialize)()
        return pixel_data

