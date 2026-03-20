from modulos.utilitario.viewset import RestViewSet
from rest_framework.permissions import IsAuthenticated
from .models import ResponsableAlmacen
from .serializers import ResponsableAlmacenSerializer

class ResponsableViewSet(RestViewSet):
    queryset = ResponsableAlmacen.objects.filter(activo=True).select_related('almacen', 'usuario')
    serializer_class = ResponsableAlmacenSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(creado_por=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(modificado_por=self.request.user)