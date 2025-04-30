# app/routes/__init__.py
from .test import test_bp
from .poi import poi_bp
from .auth import auth_bp
from .user import user_bp

__all__ = ['test_bp', 'poi_bp', 'auth_bp', 'user_bp']
