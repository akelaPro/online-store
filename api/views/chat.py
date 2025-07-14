from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from api.models.chat.models import ChatRoom, Message
from api.serializers.chat_serializer import ChatRoomSerializer, MessageSerializer


User = get_user_model()

class ChatRoomViewSet(viewsets.ModelViewSet):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return ChatRoom.objects.filter(admin=user)
        return ChatRoom.objects.filter(user=user)

    @action(detail=False, methods=['post'])
    def start_chat(self, request):
        user = request.user
        if user.is_staff:
            return Response({"error": "Admins cannot start chats"}, status=status.HTTP_403_FORBIDDEN)
        
        # Находим свободного администратора
        admin = User.objects.filter(is_staff=True).first()
        if not admin:
            return Response({"error": "No admin available"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        chat_room = ChatRoom.objects.create(user=user, admin=admin)
        serializer = self.get_serializer(chat_room)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        chat_room = self.get_object()
        messages = chat_room.messages.all()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)