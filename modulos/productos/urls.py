from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UnidadMedidaViewSet, CategoriaProductoViewSet,
    ProductoViewSet, StockProductoViewSet,
    MovimientoStockViewSet
)

router = DefaultRouter()
router.register(r'unidades-medida', UnidadMedidaViewSet)
router.register(r'categorias-producto', CategoriaProductoViewSet)
router.register(r'productos', ProductoViewSet)
router.register(r'stocks', StockProductoViewSet)
router.register(r'movimientos-stock', MovimientoStockViewSet)

urlpatterns = [
    path('', include(router.urls)),
]