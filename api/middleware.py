from django.http import JsonResponse
from django.shortcuts import redirect
from rest_framework_simplejwt.authentication import JWTAuthentication
import logging

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
        path = request.path
        
        if any(path.startswith(exempt_path) for exempt_path in self.exempt_paths):
            return self.get_response(request)

        access_token = request.COOKIES.get('access_token')
        
        if access_token:
            try:
                request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
                auth = JWTAuthentication()
                validated_token = auth.get_validated_token(access_token)
                request.user = auth.get_user(validated_token)
            except Exception as e:
                logger.warning(f"Authentication error: {str(e)}")
                return self._handle_invalid_token(request)
        else:
            return self._handle_missing_token(request)

        return self.get_response(request)

    def _handle_invalid_token(self, request):
        logger.warning(f"Invalid token for path: {request.path}")
        if request.path.startswith('/api/'):
            return JsonResponse({'error': 'Invalid authentication token'}, status=401)
        return redirect('/login/')

    def _handle_missing_token(self, request):
        logger.warning(f"Missing token for path: {request.path}")
        if request.user.is_authenticated:
            from django.contrib.auth import logout
            logout(request)
        if request.path.startswith('/api/'):
            return JsonResponse({'error': 'Authentication required'}, status=401)
        return redirect('/login/')