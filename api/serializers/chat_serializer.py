from rest_framework import serializers

from django.contrib.auth import get_user_model

from api.models.chat.models import ChatRoom, Message

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer()
    
    class Meta:
        model = Message
        fields = ['id', 'sender', 'content', 'timestamp', 'is_read']

class ChatRoomSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    admin = UserSerializer()
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = ChatRoom
        fields = ['id', 'user', 'admin', 'created_at', 'is_active', 'messages']