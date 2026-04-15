#!/usr/bin/env python
import os
import sys

def switch_environment(env='development'):
    """Cambia entre entornos de desarrollo y producción"""
    
    env_file = '.env'
    
    if not os.path.exists(env_file):
        print("❌ Archivo .env no encontrado")
        return
    
    # Leer archivo .env
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    # Modificar la línea DJANGO_ENV
    new_lines = []
    modified = False
    
    for line in lines:
        if line.startswith('DJANGO_ENV='):
            new_lines.append(f'DJANGO_ENV={env}\n')
            modified = True
        else:
            new_lines.append(line)
    
    if not modified:
        new_lines.insert(0, f'DJANGO_ENV={env}\n')
    
    # Escribir archivo
    with open(env_file, 'w') as f:
        f.writelines(new_lines)
    
    print(f"✅ Entorno cambiado a: {env.upper()}")
    
    if env == 'production':
        print("\n⚠️  ADVERTENCIA:")
        print("   - DEBUG=False")
        print("   - SSL activado")
        print("   - Recolecta archivos estáticos: python manage.py collectstatic --noinput")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] in ['development', 'production']:
        switch_environment(sys.argv[1])
    else:
        print("Uso: python switch_env.py [development|production]")
        print("Ejemplo: python switch_env.py development")