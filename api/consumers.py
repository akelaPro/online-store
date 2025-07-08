import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get("user")
        
        # Проверяем аутентификацию
        if isinstance(self.user, AnonymousUser):
            logger.warning("Rejecting anonymous connection")
            await self.close(code=4001)  # Кастомный код для ошибки аутентификации
            return

        self.room_name = "admin_chat"
        self.room_group_name = f"chat_{self.room_name}"
        
        try:
            # Добавляем в группу
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
            logger.info(f"User {self.user.username} connected to chat")
            
            # Кешируем данные пользователя
            await self.cache_user_data()
            
        except Exception as e:
            logger.error(f"Connection error: {e}")
            await self.close(code=4002)  # Кастомный код для ошибки соединения

    async def disconnect(self, close_code):
        # Проверяем, что атрибуты существуют перед попыткой их использования
        if hasattr(self, "room_group_name") and hasattr(self, "channel_name"):
            try:
                await self.channel_layer.group_discard(
                    self.room_group_name,
                    self.channel_name
                )
                logger.info(f"User {self.user.username} disconnected, code: {close_code}")
            except Exception as e:
                logger.error(f"Disconnect error: {e}")

    @database_sync_to_async
    def cache_user_data(self):
        """Кеширует данные пользователя для уменьшения запросов к БД"""
        cache_key = f"user_{self.user.id}_ws"
        cache.set(cache_key, {
            'id': self.user.id,
            'username': self.user.username,
            'is_staff': self.user.is_staff
        }, timeout=3600)

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