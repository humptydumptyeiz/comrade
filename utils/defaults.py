import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
LOG_DIR = os.path.join(BASE_DIR, 'logs')

HTTP_SERVER_PORT = 9996

LOCAL_TIMEZONE = 'Asia/Kolkata'

STATIC_FOLDER = os.path.join(BASE_DIR, 'static')