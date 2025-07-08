from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.models.chat.models import ChatMessage
from api.serializers.chat_serializer import ChatMessageSerializer


class ChatViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return ChatMessage.objects.filter(sender=user) | ChatMessage.objects.filter(sender__is_staff=True)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        
        # Помечаем сообщения как прочитанные
        unread_messages = queryset.filter(is_read=False).exclude(sender=request.user)
        unread_messages.update(is_read=True)
        
        return Response(serializer.data)