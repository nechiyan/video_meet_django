from channels.generic.websocket import AsyncWebsocketConsumer
import json
import logging

logger = logging.getLogger(__name__)

class SignalingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"room_{self.room_name}"

        logger.info(f"🔗 WebSocket Connecting: {self.room_group_name} (Channel: {self.channel_name})")

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        logger.info(f"✅ WebSocket Accepted: {self.room_group_name}")

    async def disconnect(self, close_code):
        logger.warning(f"🔴 WebSocket Disconnected: {self.room_group_name} (Code: {close_code})")

        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        logger.info(f"📩 Message Received: {text_data}")

        try:
            data = json.loads(text_data)
            message_type = data.get("type")

            if message_type == "chat_message":
                await self.relay_chat_message(data)
            elif message_type == "relay_join":
                await self.relay_join(data)

        except Exception as e:
            logger.error(f"❌ Error Processing Message: {e}")

    async def relay_chat_message(self, data):
        """Relays a chat message to all clients in the room."""
        logger.info(f"💬 Relaying Chat Message: {data}")

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": data["message"],
                "sender": data["sender"],
            }
        )

    async def chat_message(self, event):
        """Sends the chat message to the frontend."""
        logger.info(f"📤 Sending Chat Message: {event}")

        await self.send(text_data=json.dumps(event))

    async def relay_join(self, data):
        """Relays a join message to all users."""
        logger.info(f"🔄 Relaying Join Message: {data}")

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "relay_join_message",
                "message": data["message"],
            }
        )

    async def relay_join_message(self, event):
        """Sends the join message to the frontend."""
        logger.info(f"📤 Sending Join Message: {event}")

        await self.send(text_data=json.dumps(event))
