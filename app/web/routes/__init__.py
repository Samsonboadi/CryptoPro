# app/web/routes/__init__.py
"""
Web routes package
"""

from .api_routes import create_api_routes
from .websocket_routes import create_websocket_routes

__all__ = [
    'create_api_routes',
    'create_websocket_routes'
]