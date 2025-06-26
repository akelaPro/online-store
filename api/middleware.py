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
            '/static/',  # Add this line to exempt all static files
            '/media/',   # Add this line to exempt all media files
            '/api/auth/jwt/create/',
            '/api/auth/jwt/refresh/',
            '/api/auth/register/',
        ]

    def __call__(self, request):
        # Логируем входящий запрос
        logger.debug(f"\nIncoming request: {request.method} {request.path}")
        logger.debug(f"Cookies: {request.COOKIES}")
        logger.debug(f"Headers: {dict(request.headers)}")

        # Пропускаем аутентификацию для определенных путей
        if any(request.path.startswith(path) for path in self.exempt_paths):
            logger.debug(f"Path {request.path} is exempt from auth")
            return self.get_response(request)

        # Проверяем JWT токен
        access_token = request.COOKIES.get('access_token')
        
        if access_token:
            logger.debug(f"Found access token: {access_token[:10]}...")
            try:
                auth = JWTAuthentication()
                validated_token = auth.get_validated_token(access_token)
                request.user = auth.get_user(validated_token)
                logger.debug(f"Authenticated as user: {request.user.id}")
            except InvalidToken as e:
                logger.warning(f"Invalid token: {str(e)}")
                return self._handle_invalid_token(request)
            except TokenError as e:
                logger.error(f"Token error: {str(e)}")
                return self._handle_invalid_token(request)
            except Exception as e:
                logger.error(f"Unexpected error during authentication: {str(e)}", exc_info=True)
                return self._handle_invalid_token(request)
        else:
            logger.warning("No access token found in cookies")
            return self._handle_missing_token(request)

        response = self.get_response(request)
        return response

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