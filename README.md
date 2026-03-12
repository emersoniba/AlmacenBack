# Sistema de Gestión de Almacén e Inventario

Sistema backend desarrollado con Django REST Framework para la gestión de almacenes, inventario y solicitudes con aprobación. Incluye autenticación JWT, manejo de roles y permisos, con una estructura modular y escalable.

## 📋 Requisitos Previos

- Python 3.10+
- PostgreSQL (opcional, por defecto SQLite)
- pip (gestor de paquetes de Python)
- virtualenv (recomendado)
- Git

## 🚀 Instalación Rápida

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd BackendAlmacen
```
### 2. Crear entorno virtual
### Windows
```bash
python -m venv venv
venv\Scripts\activate
```
### Linux/Mac
```bash
python3 -m venv venv
source venv/bin/activate
```
### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 5. Realizar migraciones
```bash
python manage.py makemigrations
python manage.py migrate
```
### 6. Estructura del proyecto
backend/
├── almacen/                    # Configuración principal
│   ├── settings/               # Configuraciones por entorno
│   │   ├── base.py            # Configuración base
│   │   ├── development.py      # Configuración desarrollo
│   │   └── production.py       # Configuración producción
│   └── urls.py                 # URLs principales
├── modulos/                    # Módulos de la aplicación
│   ├── utilitario/             # Módulo utilitario base
│   │   ├── models.py           # Modelos base (AuditoriaBase)
│   │   ├── response.py         # Respuestas estandarizadas
│   │   └── viewset.py          # ViewSet base personalizado
│   └── users/                  # Módulo de usuarios
│       ├── models.py           # Modelos (Usuario, Persona, Rol)
│       ├── serializers.py      # Serializers
│       ├── views.py            # Vistas y ViewSets
│       └── urls.py             # URLs del módulo
├── media/                       # Archivos subidos (imágenes)
├── manage.py                    # Script de gestión
└── requirements.txt             # Dependencias

## 📧 Contacto
Email: emersonantonio666@gmail.com

GitHub: @tu-usuario

## ✨ Agradecimientos
```bash
Django REST Framework

Simple JWT

DRF Spectacular

PostgreSQL

