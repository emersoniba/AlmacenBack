from rest_framework import serializers
from .models import ResponsableAlmacen

class ResponsableAlmacenSerializer(serializers.ModelSerializer):
    almacen_nombre = serializers.CharField(source='almacen.nombre', read_only=True)
    almacen_sigla = serializers.CharField(source='almacen.sigla', read_only=True)
    usuario_nombre = serializers.CharField(source='usuario.get_full_name', read_only=True)
    usuario_username = serializers.CharField(source='usuario.username', read_only=True)
    
    class Meta:
        model = ResponsableAlmacen
        fields = [
            'id', 'almacen', 'almacen_nombre', 'almacen_sigla',
            'usuario', 'usuario_nombre', 'usuario_username',
            'fecha_desde', 'fecha_hasta', 'activo',
            'creado_por', 'fecha_creacion'
        ]
        read_only_fields = ['creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion']