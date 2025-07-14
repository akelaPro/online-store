from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatRoom(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_rooms')
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_chat_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    @classmethod
    def get_or_create_for_user(cls, user):
        try:
            # Пытаемся найти существующую комнату
            room = cls.objects.filter(user=user).first()
            if room:
                return room
                
            # Если комнаты нет - создаем новую
            admin = User.objects.filter(is_superuser=True).first()
            if not admin:
                raise ValueError("No admin user found")
                
            room = cls.objects.create(user=user, admin=admin)
            return room
            
        except Exception as e:
            print(f"Error in get_or_create_for_user: {e}")
            raise

class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)