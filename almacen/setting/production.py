from .base import *

# Debug desactivado en producción
DEBUG = False

# Base de datos para producción
DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.postgresql'),
        'NAME': os.getenv('DB_NAME_PROD', 'almacen_db_prod'),
        'USER': os.getenv('DB_USER_PROD', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD_PROD', '1234'),
        'HOST': os.getenv('DB_HOST_PROD', 'localhost'),
        'PORT': os.getenv('DB_PORT_PROD', '5432'),
    }
}

# CORS para producción
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS_PROD', 'https://tudominio.com').split(',')

# Security settings para producción
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True