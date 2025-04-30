# app/__init__.py
from flask import Flask
from .config import Config
from .extensions import db, cors
from flask import Flask
from flask_session import Session
from .extensions import db, cors, socketio
from app.extensions import cache


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    cors.init_app(app, supports_credentials=True)  # 允许跨域携带 Cookie
    Session(app)  # 启用 session
    socketio.init_app(app)
    cache.init_app(app)

    # 注册蓝图
    from .routes import test_bp, poi_bp, auth_bp, user_bp
    app.register_blueprint(test_bp, url_prefix="/api/test")
    app.register_blueprint(poi_bp, url_prefix="/api/poi")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(user_bp, url_prefix="/api/user")

    return app
