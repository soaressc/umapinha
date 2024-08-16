from datetime import timedelta
import os

class Config:
    SECRET_KEY = os.urandom(24)
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:0899@127.0.0.1/umapinha'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30) # Sessão cai após 30 minutos inativo
    SESSION_COOKIE_SECURE = True # Armazenar sessão com cookies