from pathlib import Path
from .base import *

DEBUG = True


BASE_DIR = Path(__file__).resolve().parent.parent

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'nuevo_db', 
        'USER': 'postgres',           
        'PASSWORD': '1234',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}