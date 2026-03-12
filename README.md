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
📦 backend
├── 📁 almacen
│   ├── 📁 settings
│   │   ├── 📄 base.py
│   │   ├── 📄 development.py
│   │   └── 📄 production.py
│   └── 📄 urls.py
├── 📁 modulos
│   ├── 📁 utilitario
│   │   ├── 📄 models.py
│   │   ├── 📄 response.py
│   │   └── 📄 viewset.py
│   └── 📁 users
│       ├── 📄 models.py
│       ├── 📄 serializers.py
│       └── 📄 views.py
├── 📁 media
├── 📄 manage.py
└── 📄 requirements.txt
## 📧 Contacto
Email: emersonantonio666@gmail.com

GitHub: @tu-usuario

## ✨ Agradecimientos
```bash
Django REST Framework

Simple JWT

DRF Spectacular

PostgreSQL

