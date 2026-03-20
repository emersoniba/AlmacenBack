from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UnidadMedidaViewSet, 
    CategoriaProductoViewSet, 
    ProductoViewSet,
    StockProductoViewSet
)

router = DefaultRouter()
router.register(r'unidades-medida', UnidadMedidaViewSet)
router.register(r'categorias-producto', CategoriaProductoViewSet)
router.register(r'productos', ProductoViewSet)
router.register(r'stocks', StockProductoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]