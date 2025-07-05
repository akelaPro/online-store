from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import status
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import generics, permissions

from api.serializers.registerSerializer import RegistrationSerializer


User = get_user_model()

class RegistrationAPIView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.AllowAny]  # Разрешить любому пользователю регистрироваться

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class CookieTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            access_token = response.data['access']
            refresh_token = response.data['refresh']
            
            response.set_cookie(
                key='access_token',
                value=access_token,
                httponly=True,
                secure=True,
                samesite='Lax',
                max_age=60 * 60,  # 1 час
            )
            
            response.set_cookie(
                key='refresh_token',
                value=refresh_token,
                httponly=True,
                secure=True,
                samesite='Lax',
                max_age=24 * 60 * 60,  # 1 день
            )
            
            
        return response

class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')
        
        if refresh_token:
            request.data['refresh'] = refresh_token
        
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            access_token = response.data['access']
            
            response.set_cookie(
                key='access_token',
                value=access_token,
                httponly=True,
                secure=True,
                samesite='Lax',
                max_age=60 * 60,  # 1 час
            )
            
            del response.data['access']
            
        return response

class AuthCheckView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({
            'is_authenticated': True,
            'username': request.user.username,
        })




from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh') or request.COOKIES.get('refresh_token')
            
            if refresh_token:
                try:
                    token = RefreshToken(refresh_token)
                    token.blacklist()
                except Exception as e:
                    # Даже если не удалось добавить в черный список, продолжаем
                    pass
                
            response = Response(
                {'detail': 'Successfully logged out.'},
                status=status.HTTP_200_OK
            )
            
            # Очищаем все возможные куки
            response.delete_cookie('access_token', path='/', domain=None)
            response.delete_cookie('refresh_token', path='/', domain=None)
            response.delete_cookie('csrftoken', path='/', domain=None)
            response.delete_cookie('sessionid', path='/', domain=None)
            
            # Добавляем заголовки, чтобы предотвратить кэширование
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            
            return response
            
        except Exception as e:
            return Response(
                {'detail': 'Could not log out.'},
                status=status.HTTP_400_BAD_REQUEST
            )