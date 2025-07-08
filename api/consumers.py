import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.cache import cache
from django.contrib.auth.models import AnonymousUser

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        
        if isinstance(self.user, AnonymousUser):
            logger.warning("Anonymous connection attempt rejected")
            await self.close()
            return

        self.room_name = 'admin_chat'
        self.room_group_name = f'chat_{self.room_name}'
        self.user_cache_key = f"user_{self.user.id}_ws"

        # Добавляем в группу
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        logger.info(f"User {self.user.username} connected to chat")

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            logger.info(f"User {self.user.username} disconnected")
        except Exception as e:
            logger.error(f"Disconnect error: {e}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message = data.get('message')
            
            if not message:
                return

            # Отправляем сообщение в группу
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat.message",
                    "message": message,
                    "sender_id": self.user.id,
                    "sender_name": self.user.username,
                }
            )
            
            # Сохраняем в базу
            await self.save_message(self.user.id, message)

        except json.JSONDecodeError:
            logger.error("Invalid JSON received")
        except Exception as e:
            logger.error(f"Receive error: {e}")

    async def chat_message(self, event):
        try:
            await self.send(text_data=json.dumps({
                "message": event["message"],
                "sender": event["sender_name"],
                "is_admin": await self.is_admin(event["sender_id"])
            }))
        except Exception as e:
            logger.error(f"Message send error: {e}")

    @database_sync_to_async
    def save_message(self, user_id, message):
        from .models import ChatMessage
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        user = User.objects.get(id=user_id)
        ChatMessage.objects.create(sender=user, message=message)

    @database_sync_to_async
    def is_admin(self, user_id):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            user = User.objects.get(id=user_id)
            return user.is_staff
        except User.DoesNotExist:
            return False