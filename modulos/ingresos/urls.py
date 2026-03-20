from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EstadoIngresoViewSet, IngresoViewSet, IngresoDetalleViewSet

router = DefaultRouter()
router.register(r'estados-ingreso', EstadoIngresoViewSet)
router.register(r'ingresos', IngresoViewSet)
router.register(r'ingresos-detalle', IngresoDetalleViewSet)

urlpatterns = [
    path('', include(router.urls)),
]