from channels.db import database_sync_to_async
from rest_framework_simplejwt.authentication import JWTAuthentication
import logging
from http.cookies import SimpleCookie

logger = logging.getLogger(__name__)

class JWTAuthWebsocketMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        path = scope.get('path', '')
        exempt_paths = ['/ws/login/', '/ws/register/']

        if any(path.startswith(exempt_path) for exempt_path in exempt_paths):
            return await self.app(scope, receive, send)

        cookies = {}
        headers = dict(scope.get('headers', []))
        if b'cookie' in headers:
            cookie = SimpleCookie()
            cookie.load(headers[b'cookie'].decode('utf-8'))
            cookies = {k: v.value for k, v in cookie.items()}
        
        access_token = cookies.get('access_token')
        
        if not access_token:
            logger.warning(f"Missing token for WebSocket connection: {path}")
            await send({'type': 'websocket.close', 'code': 4001})
            return
        
        try:
            auth = JWTAuthentication()
            validated_token = auth.get_validated_token(access_token)
            user = await database_sync_to_async(auth.get_user)(validated_token)
            scope['user'] = user
            return await self.app(scope, receive, send)
        except Exception as e:
            logger.warning(f"WebSocket authentication error: {str(e)}")
            await send({'type': 'websocket.close', 'code': 4001})
            return