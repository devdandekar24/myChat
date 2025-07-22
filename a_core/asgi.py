import os
# Django's built-in method to get the ASGI application
from django.core.asgi import get_asgi_application
# Channels components for handling WebSocket routing
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddlewareStack

# Set the default settings module for Django (just like in manage.py or wsgi.py)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'a_core.settings')

# Get the Django ASGI app (used for HTTP protocol)
django_asgi_app = get_asgi_application()

# Import WebSocket routing patterns from your app after setting up Django app
from a_rtchat import routing

# The `application` object is the ASGI entry point for both HTTP and WebSocket protocols
application = ProtocolTypeRouter({
    # HTTP requests are handled by Django as usual
    "http": django_asgi_app,

    # WebSocket connections are handled here
    "websocket": AllowedHostsOriginValidator(  # Prevents connections from unknown hosts
        AuthMiddlewareStack(                    # Ensures that the user is authenticated and available in `scope["user"]`
            URLRouter(                          # Directs to correct consumer based on URL
                routing.websocket_urlpatterns   # List of WebSocket URL patterns defined in your routing.py
            )
        )
    ),
})
