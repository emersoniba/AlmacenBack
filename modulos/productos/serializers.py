from rest_framework import serializers
from .models import UnidadMedida, CategoriaProducto, Producto, StockProducto, MovimientoStock
from modulos.almacenes.serializers import SubAlmacenSerializer

class UnidadMedidaSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnidadMedida
        fields = ['id', 'codigo', 'nombre', 'abreviatura']

class CategoriaProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaProducto
        fields = ['id', 'nombre', 'descripcion']

class StockProductoSerializer(serializers.ModelSerializer):
    subalmacen_nombre = serializers.CharField(source='subalmacen.nombre', read_only=True)
    subalmacen_sigla = serializers.CharField(source='subalmacen.sigla', read_only=True)
    almacen_nombre = serializers.CharField(source='subalmacen.almacen.nombre', read_only=True)
    
    class Meta:
        model = StockProducto
        fields = [
            'id', 'subalmacen', 'subalmacen_nombre', 'subalmacen_sigla',
            'almacen_nombre', 'cantidad', 'ubicacion',
            'fecha_ultimo_ingreso', 'fecha_ultimo_egreso'
        ]

class MovimientoStockSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    subalmacen_nombre = serializers.CharField(source='subalmacen.nombre', read_only=True)
    creado_por_nombre = serializers.CharField(source='creado_por.username', read_only=True)
    
    class Meta:
        model = MovimientoStock
        fields = [
            'id', 'producto', 'producto_nombre', 'subalmacen', 'subalmacen_nombre',
            'tipo', 'cantidad', 'stock_anterior', 'stock_nuevo',
            'observacion', 'fecha_movimiento', 'creado_por', 'creado_por_nombre'
        ]

class ProductoSerializer(serializers.ModelSerializer):
    unidad_medida_nombre = serializers.CharField(source='unidad_medida.nombre', read_only=True)
    unidad_medida_abrev = serializers.CharField(source='unidad_medida.abreviatura', read_only=True)
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    
    stocks = StockProductoSerializer(many=True, read_only=True)
    stock_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    # Estadísticas
    ultimo_movimiento = serializers.SerializerMethodField()
    
    class Meta:
        model = Producto
        fields = [
            'id', 'codigo', 'nombre', 'descripcion',
            'unidad_medida', 'unidad_medida_nombre', 'unidad_medida_abrev',
            'categoria', 'categoria_nombre',
            'stock_minimo', 'stock_maximo', 'imagen',
            'activo', 'stocks', 'stock_total', 'ultimo_movimiento',
            'creado_por', 'fecha_creacion'
        ]
        read_only_fields = [
            'creado_por', 'fecha_creacion', 
            'modificado_por', 'fecha_modificacion',
            'stock_total', 'ultimo_movimiento'
        ]
    
    def get_ultimo_movimiento(self, obj):
        ultimo = obj.movimientos.order_by('-fecha_movimiento').first()
        if ultimo:
            return {
                'tipo': ultimo.tipo,
                'fecha': ultimo.fecha_movimiento,
                'cantidad': ultimo.cantidad,
                'subalmacen': ultimo.subalmacen.nombre
            }
        return None

class ProductoCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear productos (sin stock)"""
    class Meta:
        model = Producto
        fields = [
            'codigo', 'nombre', 'descripcion',
            'unidad_medida', 'categoria',
            'stock_minimo', 'stock_maximo', 'imagen',
            'activo'
        ]
    
    def create(self, validated_data):
        validated_data['creado_por'] = self.context['request'].user
        return super().create(validated_data)