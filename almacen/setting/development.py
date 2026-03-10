from .base import *  
from pathlib import Path

#DEBUG = config('DEBUG', cast=bool)
DEBUG = True

CORS_ALLOWED_ORIGINS = [
    "http://localhost:4200",
]
#'ENGINE': 'django.db.backends.postgresql',
BASE_DIR = Path(__file__).resolve().parent.parent.parent  

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME':  'db.Almacen',
    }

}
'''
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'nuevo_db3', 
        'USER': 'postgres',           
        'PASSWORD': '1234',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
'''