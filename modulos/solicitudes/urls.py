from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EstadoSolicitudViewSet, SolicitudViewSet

router = DefaultRouter()
router.register(r'estados-solicitud', EstadoSolicitudViewSet)
router.register(r'solicitudes', SolicitudViewSet)

urlpatterns = [
    path('', include(router.urls)),
]