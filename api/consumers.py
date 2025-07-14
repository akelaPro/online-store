import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

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
        try:
            data = json.loads(text_data)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': data['message'],
                    'sender_id': data['sender_id']
                }
            )
            await self.save_message(data['message'], data['sender_id'])
        except Exception as e:
            print('Error processing message:', e)

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def save_message(self, message, sender_id):
        from .models import ChatRoom, Message
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        room = ChatRoom.objects.get(id=self.room_id)
        sender = User.objects.get(id=sender_id)
        Message.objects.create(
            room=room,
            sender=sender,
            content=message
        )

class AdminChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.admin_group_name = 'admin_chat'

        # Join admin group
        await self.channel_layer.group_add(
            self.admin_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave admin group
        await self.channel_layer.group_discard(
            self.admin_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message')
        room_id = text_data_json.get('room_id')
        sender_id = text_data_json.get('sender_id')
        action = text_data_json.get('action')

        if action == 'new_message':
            # Forward message to specific room
            await self.channel_layer.group_send(
                f'chat_{room_id}',
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender_id': sender_id
                }
            )
        elif action == 'room_created':
            # Notify admin about new chat room
            await self.channel_layer.group_send(
                self.admin_group_name,
                {
                    'type': 'new_room_notification',
                    'room_id': room_id,
                    'user_id': sender_id
                }
            )

    async def new_room_notification(self, event):
        # Send notification about new chat room to admin
        await self.send(text_data=json.dumps({
            'type': 'new_room',
            'room_id': event['room_id'],
            'user_id': event['user_id']
        }))

    async def chat_message(self, event):
        # Send message to admin
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'sender_id': event['sender_id'],
            'room_id': self.room_id
        }))