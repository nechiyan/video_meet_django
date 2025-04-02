from channels.generic.websocket import AsyncWebsocketConsumer
import json

class SignalingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"room_{self.room_name}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get("type")

        if message_type == "relay_join":
            await self.relay_join(data) 



    async def relay_join(self, data):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "relay_join_message",
                "message": data["message"],
            }
        )

    async def relay_join_message(self, event):
        await self.send(text_data=json.dumps(event))
