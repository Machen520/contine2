# app/models/history.py
from app.extensions import db

class UserPOIHistory(db.Model):
    __tablename__ = 'user_poi_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    poi_id = db.Column(db.Integer, db.ForeignKey('pois.id'), nullable=False)
    visit_time = db.Column(db.DateTime, server_default=db.func.now())
