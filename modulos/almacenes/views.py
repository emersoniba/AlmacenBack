from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from modulos.utilitario.viewset import RestViewSet
from .models import Almacen, SubAlmacen
from .serializers import AlmacenSerializer, SubAlmacenSerializer

@extend_schema(tags=['Gestion de Almacenes'])
class AlmacenViewSet(RestViewSet):
    queryset = Almacen.objects.filter(activo=True)
    serializer_class = AlmacenSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(creado_por=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(modificado_por=self.request.user)
        
        
@extend_schema(tags=['Gestion deSub-Almacenes'])
class SubAlmacenViewSet(RestViewSet):
    queryset = SubAlmacen.objects.filter(activo=True).select_related('almacen')
    serializer_class = SubAlmacenSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(creado_por=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(modificado_por=self.request.user)