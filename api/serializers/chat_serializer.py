from rest_framework import serializers

from api.models.chat.models import ChatMessage

class ChatMessageSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField()
    timestamp = serializers.DateTimeField(format='%Y-%m-%d %H:%M')

    class Meta:
        model = ChatMessage
        fields = ['id', 'sender', 'message', 'timestamp', 'is_read']