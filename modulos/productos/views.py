from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from modulos.utilitario.viewset import RestViewSet, RestViewSetSimple
from modulos.utilitario.response import SuccessResponse, ErrorResponse
from .models import UnidadMedida, CategoriaProducto, Producto, StockProducto, MovimientoStock
from .serializers import (
    UnidadMedidaSerializer, CategoriaProductoSerializer,
    ProductoSerializer, ProductoCreateSerializer,
    StockProductoSerializer, MovimientoStockSerializer
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
    ).prefetch_related('stocks__subalmacen__almacen', 'movimientos')
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ProductoCreateSerializer
        return ProductoSerializer
    
    def perform_create(self, serializer):
        serializer.save()
    
    @action(detail=True, methods=['get'])
    def stocks(self, request, pk=None):
        """Obtener stocks del producto por subalmacén"""
        producto = self.get_object()
        stocks = producto.stocks.select_related('subalmacen__almacen').all()
        serializer = StockProductoSerializer(stocks, many=True)
        return SuccessResponse(
            message='Stocks del producto',
            data=serializer.data
        )
    
    @action(detail=True, methods=['get'])
    def movimientos(self, request, pk=None):
        """Obtener historial de movimientos del producto"""
        producto = self.get_object()
        movimientos = producto.movimientos.select_related(
            'subalmacen', 'creado_por'
        ).order_by('-fecha_movimiento')
        
        # Filtros opcionales
        subalmacen_id = request.query_params.get('subalmacen')
        if subalmacen_id:
            movimientos = movimientos.filter(subalmacen_id=subalmacen_id)
        
        serializer = MovimientoStockSerializer(movimientos, many=True)
        return SuccessResponse(
            message='Movimientos del producto',
            data=serializer.data
        )
    
    @action(detail=False, methods=['get'])
    def con_stock_bajo(self, request):
        """Productos con stock menor al mínimo"""
        productos = []
        for producto in self.get_queryset():
            if producto.stock_total < producto.stock_minimo:
                productos.append(producto)
        
        serializer = self.get_serializer(productos, many=True)
        return SuccessResponse(
            message='Productos con stock bajo',
            data=serializer.data
        )

class StockProductoViewSet(RestViewSetSimple):
    queryset = StockProducto.objects.all().select_related(
        'producto', 'subalmacen__almacen'
    )
    serializer_class = StockProductoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros
        producto_id = self.request.query_params.get('producto')
        subalmacen_id = self.request.query_params.get('subalmacen')
        
        if producto_id:
            queryset = queryset.filter(producto_id=producto_id)
        if subalmacen_id:
            queryset = queryset.filter(subalmacen_id=subalmacen_id)
        
        return queryset

class MovimientoStockViewSet(RestViewSetSimple):
    queryset = MovimientoStock.objects.all().select_related(
        'producto', 'subalmacen', 'creado_por'
    )
    serializer_class = MovimientoStockSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros
        producto_id = self.request.query_params.get('producto')
        subalmacen_id = self.request.query_params.get('subalmacen')
        tipo = self.request.query_params.get('tipo')
        
        if producto_id:
            queryset = queryset.filter(producto_id=producto_id)
        if subalmacen_id:
            queryset = queryset.filter(subalmacen_id=subalmacen_id)
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        return queryset.order_by('-fecha_movimiento')