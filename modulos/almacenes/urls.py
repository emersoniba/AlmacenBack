from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AlmacenViewSet, SubAlmacenViewSet

router = DefaultRouter()
router.register(r'almacenes', AlmacenViewSet)
router.register(r'subalmacenes', SubAlmacenViewSet)

urlpatterns = [
    path('', include(router.urls)),
]