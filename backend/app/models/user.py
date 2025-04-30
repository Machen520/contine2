# app/models/user.py
from app.extensions import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    preferences = db.Column(db.Text)  # JSON格式字符串
    created_at = db.Column(db.DateTime, server_default=db.func.now())
