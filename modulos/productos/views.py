from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from modulos.utilitario.viewset import RestViewSet,RestViewSetSimple
from modulos.utilitario.response import SuccessResponse, ErrorResponse
from .models import UnidadMedida, CategoriaProducto, Producto, StockProducto
from .serializers import (
    UnidadMedidaSerializer, CategoriaProductoSerializer,
    ProductoSerializer, StockProductoSerializer
)

class UnidadMedidaViewSet(RestViewSetSimple):
    queryset = UnidadMedida.objects.all()
    serializer_class = UnidadMedidaSerializer
    permission_classes = [IsAuthenticated]

class CategoriaProductoViewSet(RestViewSetSimple):
    queryset = CategoriaProducto.objects.all()
    serializer_class = CategoriaProductoSerializer
    permission_classes = [IsAuthenticated]

class ProductoViewSet(RestViewSet):
    queryset = Producto.objects.filter(activo=True).select_related(
        'unidad_medida', 'categoria'
    ).prefetch_related('stocks_set__subalmacen__almacen')
    serializer_class = ProductoSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(creado_por=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(modificado_por=self.request.user)
    
    @action(detail=True, methods=['get'])
    def stocks(self, request, pk=None):
        producto = self.get_object()
        stocks = StockProducto.objects.filter(producto=producto).select_related('subalmacen__almacen')
        serializer = StockProductoSerializer(stocks, many=True)
        return SuccessResponse(
            message='Stocks del producto',
            data=serializer.data
        )
    
    @action(detail=True, methods=['post'])
    def ajustar_stock(self, request, pk=None):
        producto = self.get_object()
        subalmacen_id = request.data.get('subalmacen_id')
        cantidad = request.data.get('cantidad')
        motivo = request.data.get('motivo', 'Ajuste manual')
        
        if not subalmacen_id or cantidad is None:
            return ErrorResponse(
                message='Se requiere subalmacen_id y cantidad',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            stock, created = StockProducto.objects.get_or_create(
                producto=producto,
                subalmacen_id=subalmacen_id,
                defaults={'cantidad': 0}
            )
            
            stock.cantidad = cantidad
            stock.save()
            
            return SuccessResponse(
                message='Stock ajustado correctamente',
                data=StockProductoSerializer(stock).data
            )
        except Exception as e:
            return ErrorResponse(
                message='Error al ajustar stock',
                errors=str(e),
                status_code=status.HTTP_400_BAD_REQUEST
            )

class StockProductoViewSet(RestViewSet):
    queryset = StockProducto.objects.all().select_related('producto', 'subalmacen__almacen')
    serializer_class = StockProductoSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save()
    
    def perform_update(self, serializer):
        serializer.save()