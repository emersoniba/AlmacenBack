from rest_framework import serializers
from .models import EstadoIngreso, Ingreso, IngresoDetalle

class EstadoIngresoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoIngreso
        fields = ['id', 'nombre', 'codigo', 'descripcion', 'orden']

class IngresoDetalleSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    producto_codigo = serializers.CharField(source='producto.codigo', read_only=True)
    producto_unidad = serializers.CharField(source='producto.unidad_medida.abreviatura', read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = IngresoDetalle
        fields = [
            'id', 'ingreso', 'producto', 'producto_nombre', 'producto_codigo',
            'producto_unidad', 'cantidad', 'precio_unitario', 'subtotal',
            'stock_actualizado', 'fecha_actualizacion_stock'
        ]
        read_only_fields = ['stock_actualizado', 'fecha_actualizacion_stock']

class IngresoSerializer(serializers.ModelSerializer):
    # Información relacionada (solo lectura)
    proveedor_nombre = serializers.CharField(source='proveedor.razon_social', read_only=True)
    proveedor_nit = serializers.CharField(source='proveedor.nit', read_only=True)
    almacen_nombre = serializers.CharField(source='almacen.nombre', read_only=True)
    almacen_sigla = serializers.CharField(source='almacen.sigla', read_only=True)
    subalmacen_nombre = serializers.CharField(source='subalmacen.nombre', read_only=True)
    subalmacen_sigla = serializers.CharField(source='subalmacen.sigla', read_only=True)
    estado_nombre = serializers.CharField(source='estado.nombre', read_only=True)
    estado_codigo = serializers.CharField(source='estado.codigo', read_only=True)
    
    # Detalles y total
    detalles = IngresoDetalleSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()
    
    # Campos de auditoría
    creado_por_nombre = serializers.CharField(source='creado_por.username', read_only=True)
    
    class Meta:
        model = Ingreso
        fields = [
            'id', 'codigo', 'descripcion', 'comprobante', 'fecha_ingreso',
            'proveedor', 'proveedor_nombre', 'proveedor_nit',
            'almacen', 'almacen_nombre', 'almacen_sigla',
            'subalmacen', 'subalmacen_nombre', 'subalmacen_sigla',
            'gestion', 'estado', 'estado_nombre', 'estado_codigo',
            'observacion_anulacion', 'fecha_anulacion',
            'detalles', 'total',
            'creado_por', 'creado_por_nombre', 'fecha_creacion',
            'modificado_por', 'fecha_modificacion'
        ]
        read_only_fields = [
            'codigo', 'gestion', 'creado_por', 'fecha_creacion',
            'modificado_por', 'fecha_modificacion', 'fecha_anulacion'
        ]
    
    def get_total(self, obj) -> float:
        return sum(float(d.cantidad) * float(d.precio_unitario) for d in obj.detalles.all())

class IngresoCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear ingresos (con detalles)"""
    detalles = IngresoDetalleSerializer(many=True)
    
    class Meta:
        model = Ingreso
        fields = [
            'descripcion', 'comprobante', 'fecha_ingreso',
            'proveedor', 'almacen', 'subalmacen',
            'detalles'
        ]
    
    def validate_detalles(self, value):
        if not value:
            raise serializers.ValidationError("Debe incluir al menos un detalle")
        return value
    
    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles')
        
        # Generar código automático
        from django.utils import timezone
        gestion = timezone.now().year
        ultimo_ingreso = Ingreso.objects.filter(gestion=gestion).order_by('-id').first()
        
        if ultimo_ingreso and ultimo_ingreso.codigo:
            try:
                ultimo_numero = int(ultimo_ingreso.codigo.split('-')[-1])
                nuevo_numero = ultimo_numero + 1
            except (ValueError, IndexError):
                nuevo_numero = 1
        else:
            nuevo_numero = 1
        
        codigo = f"ING-{gestion}-{nuevo_numero:04d}"
        
        # Obtener estado por defecto (PENDIENTE)
        from .models import EstadoIngreso
        estado_pendiente = EstadoIngreso.objects.filter(codigo='PENDIENTE').first()
        
        # Crear ingreso
        ingreso = Ingreso.objects.create(
            **validated_data,
            codigo=codigo,
            gestion=gestion,
            estado=estado_pendiente,
            creado_por=self.context['request'].user
        )
        
        # Crear detalles (sin actualizar stock aún)
        for detalle_data in detalles_data:
            IngresoDetalle.objects.create(
                ingreso=ingreso,
                stock_actualizado=False,
                **detalle_data
            )
        
        return ingreso