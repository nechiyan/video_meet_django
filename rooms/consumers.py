# consumers.py (or wherever your WebSocket consumer is defined)
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from rooms.models import Room, RoomParticipant

class SignalingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'signaling_{self.room_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        # Remove participant from database if client_id is set
        if hasattr(self, 'client_id'):
            await self.remove_participant(self.room_id, self.client_id)
            
            # Notify others that user has left
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_left',
                    'userId': self.client_id
                }
            )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        msg_type = data.get('type')
        
        if msg_type == 'join':
            # Store the client ID and name for this connection
            self.client_id = data.get('clientId')
            name = data.get('name')
            
            # Add participant to database
            await self.add_participant(self.room_id, self.client_id, name)
            
            # Get all room participants
            participants = await self.get_room_participants(self.room_id)
            
            # Send current room users to the joining client
            await self.send(text_data=json.dumps({
                'type': 'room_users',
                'users': participants
            }))
            
            # Notify others that a new user joined
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_joined',
                    'userId': self.client_id,
                    'name': name
                }
            )
        
        # Handle other message types (offer, answer, ice_candidate, etc.)
        elif msg_type in ['offer', 'answer', 'ice_candidate', 'chat_message']:
            # Forward the message to the appropriate recipient
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': msg_type,
                    **data
                }
            )
    
    # Handler for user_joined messages
    async def user_joined(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_joined',
            'userId': event['userId'],
            'name': event['name']
        }))
    
    # Handler for user_left messages
    async def user_left(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_left',
            'userId': event['userId']
        }))
    
    # Forward other message types
    async def offer(self, event):
        await self.send(text_data=json.dumps(event))
    
    async def answer(self, event):
        await self.send(text_data=json.dumps(event))
    
    async def ice_candidate(self, event):
        await self.send(text_data=json.dumps(event))
    
    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))
    
    # Database operations
    @database_sync_to_async
    def add_participant(self, room_id, client_id, name):
        room = Room.objects.get(id=room_id)
        RoomParticipant.objects.update_or_create(
            room=room,
            client_id=client_id,
            defaults={'name': name}
        )
    
    @database_sync_to_async
    def remove_participant(self, room_id, client_id):
        room = Room.objects.get(id=room_id)
        RoomParticipant.objects.filter(room=room, client_id=client_id).delete()
    
    @database_sync_to_async
    def get_room_participants(self, room_id):
        room = Room.objects.get(id=room_id)
        participants = room.participants.all()
        return [
            {
                'id': str(participant.client_id),
                'name': participant.name
            }
            for participant in participants
        ]