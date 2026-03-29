from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db import transaction
from modulos.utilitario.viewset import RestViewSet
from modulos.utilitario.response import SuccessResponse, ErrorResponse
from .models import EstadoIngreso, Ingreso, IngresoDetalle
from .serializers import (
    EstadoIngresoSerializer, IngresoSerializer, 
    IngresoCreateSerializer, IngresoDetalleSerializer
)

@extend_schema(tags=['Estados de Ingreso'])
class EstadoIngresoViewSet(RestViewSet):
    queryset = EstadoIngreso.objects.all()
    serializer_class = EstadoIngresoSerializer
    permission_classes = [IsAuthenticated]

@extend_schema(tags=['Gestión de Ingresos'])
class IngresoViewSet(RestViewSet):
    queryset = Ingreso.objects.all().select_related(
        'proveedor', 'almacen', 'subalmacen', 'estado', 'creado_por'
    ).prefetch_related('detalles__producto')
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return IngresoCreateSerializer
        return IngresoSerializer
    
    @transaction.atomic
    def perform_create(self, serializer):
        serializer.save()
    
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def completar(self, request, pk=None):
        """Completar un ingreso y actualizar stocks"""
        ingreso = self.get_object()
        
        # Verificar estado actual
        estado_pendiente = EstadoIngreso.objects.filter(codigo='PENDIENTE').first()
        if ingreso.estado and ingreso.estado.codigo != 'PENDIENTE':
            return ErrorResponse(
                message=f'El ingreso no puede ser completado. Estado actual: {ingreso.estado.nombre}',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        if not ingreso.detalles.exists():
            return ErrorResponse(
                message='No se puede completar un ingreso sin detalles',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Actualizar stock para cada detalle
        from modulos.productos.models import StockProducto
        
        detalles_actualizados = []
        for detalle in ingreso.detalles.all():
            if not detalle.stock_actualizado:
                # Obtener o crear stock
                stock, created = StockProducto.objects.get_or_create(
                    producto=detalle.producto,
                    subalmacen=ingreso.subalmacen,
                    defaults={'cantidad': 0}
                )
                
                # Actualizar cantidad
                stock.cantidad += detalle.cantidad
                stock.fecha_ultimo_ingreso = timezone.now()
                stock.save()
                
                # Marcar detalle como actualizado
                detalle.stock_actualizado = True
                detalle.fecha_actualizacion_stock = timezone.now()
                detalle.save()
                
                detalles_actualizados.append({
                    'producto': detalle.producto.nombre,
                    'cantidad': detalle.cantidad,
                    'stock_anterior': float(stock.cantidad - detalle.cantidad),
                    'stock_nuevo': float(stock.cantidad)
                })
        
        # Cambiar estado
        estado_completado = EstadoIngreso.objects.filter(codigo='COMPLETADO').first()
        ingreso.estado = estado_completado
        ingreso.save()
        
        return SuccessResponse(
            message='Ingreso completado exitosamente',
            data={
                'ingreso': IngresoSerializer(ingreso).data,
                'stocks_actualizados': detalles_actualizados
            }
        )
    
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def anular(self, request, pk=None):
        """Anular un ingreso y revertir stocks"""
        ingreso = self.get_object()
        observacion = request.data.get('observacion', '')
        
        # Verificar estado actual
        if not ingreso.estado or ingreso.estado.codigo not in ['PENDIENTE', 'COMPLETADO']:
            return ErrorResponse(
                message='No se puede anular este ingreso',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Si estaba completado, revertir stocks
        if ingreso.estado.codigo == 'COMPLETADO':
            from modulos.productos.models import StockProducto
            
            for detalle in ingreso.detalles.filter(stock_actualizado=True):
                try:
                    stock = StockProducto.objects.get(
                        producto=detalle.producto,
                        subalmacen=ingreso.subalmacen
                    )
                    stock.cantidad -= detalle.cantidad
                    stock.save()
                except StockProducto.DoesNotExist:
                    pass
                
                detalle.stock_actualizado = False
                detalle.save()
        
        # Cambiar estado
        estado_anulado = EstadoIngreso.objects.filter(codigo='ANULADO').first()
        ingreso.estado = estado_anulado
        ingreso.observacion_anulacion = observacion
        ingreso.fecha_anulacion = timezone.now()
        ingreso.save()
        
        return SuccessResponse(
            message='Ingreso anulado exitosamente',
            data=IngresoSerializer(ingreso).data
        )
    
    @action(detail=True, methods=['post'])
    def agregar_detalle(self, request, pk=None):
        """Agregar un detalle a un ingreso pendiente"""
        ingreso = self.get_object()
        
        # Verificar estado
        if ingreso.estado and ingreso.estado.codigo != 'PENDIENTE':
            return ErrorResponse(
                message='No se pueden agregar detalles a un ingreso no pendiente',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = IngresoDetalleSerializer(data=request.data)
        if not serializer.is_valid():
            return ErrorResponse(
                message='Error en los datos del detalle',
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Guardar detalle (sin actualizar stock aún)
        detalle = IngresoDetalle.objects.create(
            ingreso=ingreso,
            stock_actualizado=False,
            **serializer.validated_data
        )
        
        return SuccessResponse(
            message='Detalle agregado exitosamente',
            data=IngresoDetalleSerializer(detalle).data,
            status_code=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['delete'])
    def quitar_detalle(self, request, pk=None):
        """Eliminar un detalle de un ingreso pendiente"""
        ingreso = self.get_object()
        
        # Verificar estado
        if ingreso.estado and ingreso.estado.codigo != 'PENDIENTE':
            return ErrorResponse(
                message='No se pueden eliminar detalles de un ingreso no pendiente',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        detalle_id = request.query_params.get('detalle_id')
        if not detalle_id:
            return ErrorResponse(
                message='Se requiere detalle_id',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            detalle = ingreso.detalles.get(id=detalle_id)
            detalle.delete()
            
            return SuccessResponse(
                message='Detalle eliminado exitosamente'
            )
        except IngresoDetalle.DoesNotExist:
            return ErrorResponse(
                message='Detalle no encontrado',
                status_code=status.HTTP_404_NOT_FOUND
            )

class IngresoDetalleViewSet(RestViewSet):
    queryset = IngresoDetalle.objects.all().select_related('ingreso', 'producto')
    serializer_class = IngresoDetalleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        ingreso_id = self.request.query_params.get('ingreso')
        if ingreso_id:
            queryset = queryset.filter(ingreso_id=ingreso_id)
        return queryset