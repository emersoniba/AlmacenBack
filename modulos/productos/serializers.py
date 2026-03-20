from rest_framework import serializers
from .models import UnidadMedida, CategoriaProducto, Producto, StockProducto
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
            'almacen_nombre', 'cantidad', 'ubicacion', 'fecha_ultimo_movimiento'
        ]

class ProductoSerializer(serializers.ModelSerializer):
    unidad_medida_nombre = serializers.CharField(source='unidad_medida.nombre', read_only=True)
    unidad_medida_abrev = serializers.CharField(source='unidad_medida.abreviatura', read_only=True)
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    stocks = StockProductoSerializer(source='stocks_set', many=True, read_only=True)
    stock_total = serializers.SerializerMethodField()
    
    class Meta:
        model = Producto
        fields = [
            'id', 'codigo', 'nombre', 'descripcion',
            'unidad_medida', 'unidad_medida_nombre', 'unidad_medida_abrev',
            'categoria', 'categoria_nombre',
            'stock_minimo', 'stock_maximo', 'imagen',
            'activo', 'stocks', 'stock_total',
            'creado_por', 'fecha_creacion'
        ]
        read_only_fields = ['creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion']
    
    def get_stock_total(self, obj)->float:
        return sum(stock.cantidad for stock in obj.stocks_set.all())
    
    def create(self, validated_data):
        producto = super().create(validated_data)
        # No crear stock inicial, se creará con los ingresos
        return producto