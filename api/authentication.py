from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings
import logging
from django.http import JsonResponse
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.conf import settings

logger = logging.getLogger(__name__)



class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # Получаем токен из куки
        raw_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE'])
        
        logger.debug(f"CookieJWTAuthentication - Checking token for path: {request.path}")
        logger.debug(f"Raw token from cookies: {'exists' if raw_token else 'not found'}")
        
        if raw_token is None:
            logger.debug("No token found in cookies")
            return None
            
        try:
            validated_token = self.get_validated_token(raw_token)
            user = self.get_user(validated_token)
            logger.debug(f"Successfully authenticated user: {user.id}")
            return user, validated_token
        except InvalidToken as e:
            logger.warning(f"Invalid token error: {str(e)}")
            return None
        except TokenError as e:
            logger.error(f"Token error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected authentication error: {str(e)}", exc_info=True)
            return None