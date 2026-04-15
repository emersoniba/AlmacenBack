#!/bin/bash

echo "🚀 Iniciando build en Render..."

# Instalar dependencias
pip install -r requirements.txt

# Recolectar archivos estáticos
python manage.py collectstatic --noinput

# Ejecutar migraciones
python manage.py migrate

echo "✅ Build completado exitosamente"