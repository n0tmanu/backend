import asyncio
from django.core.asgi import get_asgi_application

# Set up the event loop
asyncio.set_event_loop(asyncio.new_event_loop())

# Get the ASGI application
django_asgi_app = get_asgi_application()

# Run the ASGI application
def application(scope, receive, send):
    return django_asgi_app(scope, receive, send)
