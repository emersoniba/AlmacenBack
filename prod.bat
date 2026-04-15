@echo off
echo ========================================
echo Cambiando a entorno de PRODUCCIÓN
echo ========================================
python switch_env.py production
echo.
echo Ejecuta: python manage.py runserver --insecure
echo O mejor: gunicorn almacen.wsgi:application
pause..