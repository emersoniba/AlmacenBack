from rest_framework import serializers
from .models import Proveedor

class ProveedorSerializer(serializers.ModelSerializer):
    # Campos de auditoría legibles
    creado_por_nombre = serializers.CharField(
        source='creado_por.username', 
        read_only=True,
        default=None
    )
    modificado_por_nombre = serializers.CharField(
        source='modificado_por.username', 
        read_only=True,
        default=None
    )
    eliminado_por_nombre = serializers.CharField(
        source='eliminado_por.username', 
        read_only=True,
        default=None
    )
    
    class Meta:
        model = Proveedor
        fields = '__all__'  # Esto ya incluye todos los campos de AuditoriaBase
        read_only_fields = [
            'creado_por', 'fecha_creacion', 
            'modificado_por', 'fecha_modificacion',
            'eliminado_por', 'fecha_eliminacion'
        ]