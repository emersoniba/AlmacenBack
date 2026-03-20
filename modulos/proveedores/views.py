from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from modulos.utilitario.viewset import RestViewSet
from modulos.utilitario.response import SuccessResponse, ErrorResponse
from .models import Proveedor
from .serializers import ProveedorSerializer

class ProveedorViewSet(RestViewSet):
    # Solo mostrar proveedores activos
    queryset = Proveedor.objects.filter(activo=True)
    serializer_class = ProveedorSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        """Al crear, guardamos quién lo creó y fecha de creación"""
        serializer.save(
            creado_por=self.request.user,
            fecha_creacion=timezone.now()
        )
    
    def perform_update(self, serializer):
        """Al actualizar, guardamos quién lo modificó y fecha de modificación"""
        serializer.save(
            modificado_por=self.request.user,
            fecha_modificacion=timezone.now()
        )
    
    def destroy(self, request, *args, **kwargs):
        """
        Sobrescribimos el método destroy para hacer eliminado lógico
        en lugar de eliminado físico
        """
        try:
            instance = self.get_object()
            
            # Eliminado lógico
            instance.activo = False
            instance.eliminado_por = request.user
            instance.fecha_eliminacion = timezone.now()
            instance.save()
            
            return SuccessResponse(
                message='Proveedor eliminado correctamente',
                data={'id': instance.id}
            )
        except Exception as e:
            return ErrorResponse(
                message='Error al eliminar proveedor',
                errors=str(e),
                status_code=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def restaurar(self, request, pk=None):
        """Endpoint para restaurar un proveedor eliminado"""
        try:
            # Buscar incluyendo inactivos
            instance = Proveedor.objects.filter(id=pk).first()
            if not instance:
                return ErrorResponse(
                    message='Proveedor no encontrado',
                    status_code=status.HTTP_404_NOT_FOUND
                )
            
            instance.activo = True
            instance.modificado_por = request.user
            instance.fecha_modificacion = timezone.now()
            instance.save()
            
            return SuccessResponse(
                message='Proveedor restaurado correctamente',
                data=ProveedorSerializer(instance).data
            )
        except Exception as e:
            return ErrorResponse(
                message='Error al restaurar proveedor',
                errors=str(e),
                status_code=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def eliminados(self, request):
        """Endpoint para listar proveedores eliminados"""
        eliminados = Proveedor.objects.filter(activo=False)
        serializer = self.get_serializer(eliminados, many=True)
        return SuccessResponse(
            message='Proveedores eliminados',
            data=serializer.data
        )