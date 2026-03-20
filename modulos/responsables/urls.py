from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ResponsableViewSet

router = DefaultRouter()
router.register(r'responsables', ResponsableViewSet)

urlpatterns = [
    path('', include(router.urls)),
]