from channels.db import database_sync_to_async
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from game_api.models import Player
from game_api.services import create_pixel_for_player, serialize_pixel

class PixelConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("pixels", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("pixels", self.channel_name)

    async def receive(self, text_data):
        try:
            user = self.scope["user"]
            if not user.is_authenticated:
                await self.send(text_data=json.dumps({"error": "Authenticate first"}))
                return

            data = json.loads(text_data)

            player, _ = await database_sync_to_async(Player.objects.get_or_create)(user=user)
            result = await database_sync_to_async(create_pixel_for_player)(
                player,
                float(data["x"]),
                float(data["y"]),
                data.get("description", "")
            )

            if "error" in result:
                await self.send(text_data=json.dumps({"error": result["error"]}))
                return

            pixel_data = await database_sync_to_async(serialize_pixel)(result["pixel"])

            await self.channel_layer.group_send(
                "pixels",
                {"type": "pixel.update", "pixel": pixel_data}
            )
        except Exception as e:
            import traceback;
            traceback.print_exc()
            await self.send(text_data=json.dumps({"error": str(e)}))

    async def pixel_update(self, event):
        await self.send(text_data=json.dumps(event["pixel"]))
