import os
import sys

def switch_environment(env='development'):
    """Cambia entre entornos de desarrollo y producción"""
    
    settings_path = 'D:\\almacen\\BackendAlmacen\\core\\settings\\__init__.py'
    
    if env == 'development':
        content = """from .development import *\n"""
        print("🔄 Cambiando a entorno de DESARROLLO")
    elif env == 'production':
        content = """from .production import *\n"""
        print("🔄 Cambiando a entorno de PRODUCCIÓN")
    else:
        print(f"❌ Entorno inválido: {env}")
        return
    
    with open(settings_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Entorno cambiado a: {env}")
    print("💡 Recuerda: python manage.py runserver")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        switch_environment(sys.argv[1])
    else:
        print("Uso: python switch_env.py [development|production]")