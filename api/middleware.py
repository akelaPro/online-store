import logging
from django.http import JsonResponse
from django.shortcuts import redirect
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.conf import settings

logger = logging.getLogger(__name__)


class JWTAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.exempt_paths = [
            '/admin/',
            '/login/',
            '/register/',
            '/static/',
            '/media/',
            '/api/auth/jwt/create/',
            '/api/auth/jwt/refresh/',
            '/api/auth/register/',
        ]

    def __call__(self, request):
        # Пропускаем аутентификацию для определенных путей
        if any(request.path.startswith(path) for path in self.exempt_paths):
            return self.get_response(request)

        # Проверяем JWT токен
        access_token = request.COOKIES.get('access_token')
        
        if access_token:
            try:
                # Добавляем токен в заголовок Authorization для DRF
                request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
                
                auth = JWTAuthentication()
                validated_token = auth.get_validated_token(access_token)
                request.user = auth.get_user(validated_token)
            except Exception as e:
                logger.warning(f"Authentication error: {str(e)}")
                return self._handle_invalid_token(request)
        else:
            return self._handle_missing_token(request)

        response = self.get_response(request)
        return response

    # ... остальные методы остаются без изменений

    def _handle_invalid_token(self, request):
        logger.warning(f"Invalid token for path: {request.path}")
        if request.path.startswith('/api/'):
            return JsonResponse(
                {'error': 'Invalid authentication token'}, 
                status=401
            )
        return redirect('/login/')

    def _handle_missing_token(self, request):
        logger.warning(f"Missing token for path: {request.path}")
        if request.path.startswith('/api/'):
            return JsonResponse(
                {'error': 'Authentication required'}, 
                status=401
            )
        return redirect('/login/')