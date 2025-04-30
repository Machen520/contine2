# app/config.py
class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@localhost:3306/poi_query_system'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'your_secret_key'

    SESSION_TYPE = 'filesystem'
    SESSION_COOKIE_HTTPONLY = False
    SESSION_COOKIE_SAMESITE = 'Lax'

    AMAP_REST_KEY = '4194c76cb632b17d74ff6144472ad27d'
