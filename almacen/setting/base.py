import os
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = "django-insecure-otpune@s+*ago&6#1brmie+a2c60usb@msa$&8#a77135n8l%0"

DEBUG = os.getenv('DJANGO_DEBUG', 'True') == 'True'
AUTH_USER_MODEL = "users.Usuario"
# ============================================
# DETECTAR ENTORNO
# ============================================
ENV = os.getenv('DJANGO_ENV', 'development')
IS_DEV = ENV == 'development'
IS_PROD = ENV == 'production'

print(f"🌍 Entorno: {ENV.upper()}")

ALLOWED_HOSTS = ["192.168.0.9", "localhost", "127.0.0.1"]


APP_BASE = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]
APP_TRIRD = [
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "drf_spectacular",
    "rest_framework_simplejwt.token_blacklist",
]
APP_LOCAL = [
    "modulos.utilitario",
    "modulos.users",
    "modulos.almacenes",
    "modulos.proveedores",
    "modulos.productos",
    "modulos.responsables",
    "modulos.ingresos",
    "modulos.solicitudes",
]
INSTALLED_APPS = APP_BASE + APP_TRIRD + APP_LOCAL

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "almacen.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "almacen.wsgi.application"

CORS_ALLOWED_ORIGINS = [
    "http://localhost:4200",  # Puerto por defecto de Angular
    "http://localhost:8081",  # Expo web react navtive
    "http://10.0.2.2:8000",  # Emulador Androidreact navtive
    "http://192.168.0.9:8000",         # Tu IP local (agregar esta línea)
    "http://192.168.0.9",  
    "http://localhost:8100", # ionic angular
    #"http://192.168.0.9:8100", # ionic angular celular prueba
]
CORS_ALLOW_ALL_ORIGINS = True

# Configuración de Django REST Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}
# ============================================
# BASE DE DATOS - Configuración dinámica
# ============================================
def get_db_config():
    """Obtener configuración de base de datos según entorno"""
    if IS_DEV:
        return {
            'ENGINE': os.getenv('DB_ENGINE_DEV', 'django.db.backends.postgresql'),
            'NAME': os.getenv('DB_NAME_DEV', 'db.Almacen'),
            'USER': os.getenv('DB_USER_DEV', 'postgres'),
            'PASSWORD': os.getenv('DB_PASSWORD_DEV', '1234'),
            'HOST': os.getenv('DB_HOST_DEV', 'localhost'),
            'PORT': os.getenv('DB_PORT_DEV', '5432'),
        }
    else:
        return {
            'ENGINE': os.getenv('DB_ENGINE_PROD', 'django.db.backends.postgresql'),
            'NAME': os.getenv('DB_NAME_PROD', 'almacen_db_prod'),
            'USER': os.getenv('DB_USER_PROD', 'postgres'),
            'PASSWORD': os.getenv('DB_PASSWORD_PROD', '1234'),
            'HOST': os.getenv('DB_HOST_PROD', 'localhost'),
            'PORT': os.getenv('DB_PORT_PROD', '5432'),
        }

DATABASES = {
    'default': get_db_config()
}

# Configuración de JWT
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=2),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    # "ACCESS_TOKEN_LIFETIME": timedelta(minutes=1),  # ⏰ Cambiado a 1 minuto
    # "REFRESH_TOKEN_LIFETIME": timedelta(minutes=2), # ⏰ 2 minutos para refresco
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}
# Configuración de Swagger / Spectacular
SPECTACULAR_SETTINGS = {
    "TITLE": "API de Almacén e Inventario",
    "DESCRIPTION": "Sistema de gestión de almacenes con aprobación de solicitudes",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}
# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
LANGUAGE_CODE = "es-bo"
TIME_ZONE = "America/La_Paz"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
