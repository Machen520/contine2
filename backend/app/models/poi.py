# app/models/poi.py
from app.extensions import db
from sqlalchemy.dialects.mysql import DOUBLE
from geoalchemy2 import Geometry


class POI(db.Model):
    __tablename__ = 'pois'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    description = db.Column(db.Text)
    latitude = db.Column(DOUBLE, nullable=False)
    longitude = db.Column(DOUBLE, nullable=False)
    rating = db.Column(db.Float, default=0.0)
    rating_count = db.Column(db.Integer, default=1)
    tags = db.Column(db.Text)
    location = db.Column(Geometry(geometry_type='POINT', srid=4326), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
