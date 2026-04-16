

import os

from django.core.wsgi import get_wsgi_application

env = os.getenv('DJANGO_ENV', 'development').lower()
settings_module = 'almacen.setting.production' if env == 'production' else 'almacen.setting.development'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

application = get_wsgi_application()
