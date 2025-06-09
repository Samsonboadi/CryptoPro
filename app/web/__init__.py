"""
Web routes package
"""
from .routes import create_api_routes
from .routes.websocket_routes import create_websocket_routes

__all__ = [
    'create_api_routes',
    'create_websocket_routes'
]