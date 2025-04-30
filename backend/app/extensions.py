# app/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_caching import Cache

db = SQLAlchemy()
cors = CORS()
socketio = SocketIO(cors_allowed_origins="*", async_mode='eventlet')  # ✅ 加上 async_mode
cache = Cache(config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_URL': 'redis://localhost:6379/0'})