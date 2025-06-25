import logging
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

logger = logging.getLogger(__name__)

class JWTAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Пропускаем только конкретные auth endpoints, а не все /api/auth/
        excluded_paths = [
            '/api/auth/jwt/create/',
            '/api/auth/jwt/refresh/',
            '/api/auth/jwt/logout/',
        ]
        
        if request.path in excluded_paths or request.path.startswith('/admin/'):
            logger.debug(f"Skipping auth for {request.path}")
            return None
            
        if request.path.startswith('/api/'):
            logger.debug(f"Processing API request to {request.path}")
            jwt_auth = JWTAuthentication()
            auth_cookie_name = settings.SIMPLE_JWT['AUTH_COOKIE']
            
            if not jwt_auth.get_header(request) and auth_cookie_name in request.COOKIES:
                token = request.COOKIES[auth_cookie_name]
                try:
                    validated_token = jwt_auth.get_validated_token(token)
                    user = jwt_auth.get_user(validated_token)
                    request.user = user
                    request.META['HTTP_AUTHORIZATION'] = f'Bearer {token}'
                    logger.info(f"Authenticated user {user.username}")
                except Exception as e:
                    logger.error(f"Auth failed: {str(e)}")
        
        return None