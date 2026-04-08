from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db import transaction
from modulos.utilitario.viewset import RestViewSet, RestViewSetSimple
from modulos.utilitario.response import SuccessResponse, ErrorResponse
from .models import EstadoSolicitud, Solicitud, DetalleSolicitud, HistorialSolicitud
from .serializers import (
    EstadoSolicitudSerializer, SolicitudListSerializer,
    SolicitudDetailSerializer, SolicitudCreateSerializer,
    SolicitudAprobarSerializer, SolicitudEntregarSerializer,
    DetalleSolicitudSerializer
)

class EstadoSolicitudViewSet(RestViewSetSimple):
    queryset = EstadoSolicitud.objects.all()
    serializer_class = EstadoSolicitudSerializer
    permission_classes = [IsAuthenticated]

class SolicitudViewSet(RestViewSet):
    queryset = Solicitud.objects.all().select_related(
        'solicitante',
        'solicitante__persona',  # <-- AGREGAR ESTO
        'aprobador',
        'aprobador__persona',    # <-- También para aprobador
        'almacenero',
        'almacenero__persona',   # <-- También para almacenero
        'almacen', 
        'subalmacen', 
        'estado'
    ).prefetch_related('detalles__producto')
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return SolicitudCreateSerializer
        elif self.action == 'retrieve':
            return SolicitudDetailSerializer
        return SolicitudListSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Filtrar según el rol del usuario
        user_roles = user.roles.values_list('nombre', flat=True)
        
        if 'SOLICITANTE' in user_roles:
            # Solicitante solo ve sus propias solicitudes
            queryset = queryset.filter(solicitante=user)
        elif 'APROBADOR' in user_roles:
            # Aprobador ve solicitudes pendientes
            estado_pendiente = EstadoSolicitud.objects.filter(codigo='PENDIENTE').first()
            queryset = queryset.filter(estado=estado_pendiente)
        elif 'ALMACENERO' in user_roles:
            # Almacenero ve solicitudes aprobadas pendientes de entrega
            estado_aprobado = EstadoSolicitud.objects.filter(codigo='APROBADO').first()
            queryset = queryset.filter(estado=estado_aprobado)
        
        return queryset
    
    @transaction.atomic
    def perform_create(self, serializer):
        serializer.save()
    
    @action(detail=True, methods=['post'])
    def enviar(self, request, pk=None):
        """Enviar solicitud para aprobación"""
        solicitud = self.get_object()
        
        # Verificar estado
        if solicitud.estado.codigo != 'PENDIENTE':
            return ErrorResponse(
                message=f'No se puede enviar. Estado actual: {solicitud.estado.nombre}',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        if not solicitud.detalles.exists():
            return ErrorResponse(
                message='No se puede enviar una solicitud sin productos',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Actualizar estado y fecha de envío
        estado_enviado = EstadoSolicitud.objects.filter(codigo='ENVIADO').first()
        if not estado_enviado:
            estado_enviado = solicitud.estado
        
        solicitud.estado = estado_enviado
        solicitud.fecha_envio = timezone.now()
        solicitud.save()
        
        # Registrar historial
        HistorialSolicitud.objects.create(
            solicitud=solicitud,
            estado_anterior=None,
            estado_nuevo=estado_enviado,
            usuario=request.user,
            observacion="Solicitud enviada para aprobación"
        )
        
        return SuccessResponse(
            message='Solicitud enviada correctamente',
            data=SolicitudListSerializer(solicitud).data
        )
    
    @action(detail=True, methods=['post'])
    def aprobar_rechazar(self, request, pk=None):
        """Aprobar o rechazar solicitud"""
        solicitud = self.get_object()
        serializer = SolicitudAprobarSerializer(data=request.data)
        
        if not serializer.is_valid():
            return ErrorResponse(
                message='Error en los datos',
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar estado
        if solicitud.estado.codigo not in ['PENDIENTE', 'ENVIADO']:
            return ErrorResponse(
                message=f'No se puede aprobar/rechazar. Estado actual: {solicitud.estado.nombre}',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        aprobar = serializer.validated_data['aprobar']
        observacion = serializer.validated_data.get('observacion', '')
        
        if aprobar:
            estado = EstadoSolicitud.objects.filter(codigo='APROBADO').first()
            solicitud.fecha_aprobacion = timezone.now()
            mensaje = "Solicitud aprobada"
        else:
            estado = EstadoSolicitud.objects.filter(codigo='RECHAZADO').first()
            solicitud.fecha_rechazo = timezone.now()
            mensaje = "Solicitud rechazada"
        
        solicitud.estado = estado
        solicitud.aprobador = request.user
        solicitud.observacion_aprobador = observacion
        solicitud.save()
        
        # Registrar historial
        HistorialSolicitud.objects.create(
            solicitud=solicitud,
            estado_anterior=solicitud.estado,
            estado_nuevo=estado,
            usuario=request.user,
            observacion=observacion
        )
        
        return SuccessResponse(
            message=mensaje,
            data=SolicitudListSerializer(solicitud).data
        )
    
    @action(detail=True, methods=['post'])
    def entregar(self, request, pk=None):
        """Entregar productos de solicitud aprobada"""
        solicitud = self.get_object()
        serializer = SolicitudEntregarSerializer(data=request.data)
        
        if not serializer.is_valid():
            return ErrorResponse(
                message='Error en los datos',
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar estado
        if solicitud.estado.codigo != 'APROBADO':
            return ErrorResponse(
                message=f'No se puede entregar. Estado actual: {solicitud.estado.nombre}',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        entregas = serializer.validated_data['entregas']
        observacion = serializer.validated_data.get('observacion', '')
        
        # Validar y actualizar entregas
        from modulos.productos.models import StockProducto, MovimientoStock
        
        for entrega in entregas:
            detalle_id = entrega.get('detalle_id')
            cantidad_entregada = entrega.get('cantidad_entregada')
            
            try:
                detalle = solicitud.detalles.get(id=detalle_id)
            except DetalleSolicitud.DoesNotExist:
                return ErrorResponse(
                    message=f'Detalle {detalle_id} no encontrado',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # Validar cantidad
            if cantidad_entregada > detalle.cantidad_solicitada:
                return ErrorResponse(
                    message=f'Cantidad entregada no puede exceder la solicitada',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # Actualizar detalle
            detalle.cantidad_entregada = cantidad_entregada
            detalle.save()
            
            # Actualizar stock si hay entrega
            if cantidad_entregada > 0:
                stock = StockProducto.objects.filter(
                    producto=detalle.producto,
                    subalmacen=solicitud.subalmacen
                ).first()
                
                if stock:
                    stock.cantidad -= cantidad_entregada
                    stock.fecha_ultimo_egreso = timezone.now()
                    stock.save()
                    
                    # Registrar movimiento
                    MovimientoStock.objects.create(
                        producto=detalle.producto,
                        subalmacen=solicitud.subalmacen,
                        tipo='EGRESO',
                        cantidad=cantidad_entregada,
                        stock_anterior=stock.cantidad + cantidad_entregada,
                        stock_nuevo=stock.cantidad,
                        observacion=f"Entrega solicitud {solicitud.codigo}",
                        creado_por=request.user
                    )
        
        # Cambiar estado
        estado_entregado = EstadoSolicitud.objects.filter(codigo='ENTREGADO').first()
        solicitud.estado = estado_entregado
        solicitud.almacenero = request.user
        solicitud.observacion_almacenero = observacion
        solicitud.fecha_recepcion = timezone.now()
        solicitud.save()
        
        # Registrar historial
        HistorialSolicitud.objects.create(
            solicitud=solicitud,
            estado_anterior=solicitud.estado,
            estado_nuevo=estado_entregado,
            usuario=request.user,
            observacion=observacion
        )
        
        return SuccessResponse(
            message='Solicitud entregada correctamente',
            data=SolicitudDetailSerializer(solicitud).data
        )
    
    @action(detail=True, methods=['get'])
    def historial(self, request, pk=None):
        """Obtener historial de cambios"""
        solicitud = self.get_object()
        historial = solicitud.historial.all().select_related('estado_anterior', 'estado_nuevo', 'usuario')
        
        data = []
        for h in historial:
            data.append({
                'id': h.id,
                'estado_anterior': h.estado_anterior.nombre if h.estado_anterior else None,
                'estado_nuevo': h.estado_nuevo.nombre,
                'usuario': h.usuario.username,
                'observacion': h.observacion,
                'fecha_cambio': h.fecha_cambio
            })
        
        return SuccessResponse(
            message='Historial de la solicitud',
            data=data
        )
    
    @action(detail=False, methods=['get'])
    @extend_schema(tags=['Solicitudes'])
    def mis_solicitudes(self, request):
        """Obtener solicitudes del usuario actual"""
        user = request.user
        solicitudes = Solicitud.objects.filter(solicitante=user).order_by('-fecha_solicitud')
        serializer = self.get_serializer(solicitudes, many=True)
        return SuccessResponse(
            message='Mis solicitudes',
            data=serializer.data
        )