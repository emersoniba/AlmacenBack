from rest_framework import serializers
from .models import Almacen, SubAlmacen

class AlmacenSerializer(serializers.ModelSerializer):
    subalmacenes_count = serializers.IntegerField(source='subalmacenes.count', read_only=True)
    
    class Meta:
        model = Almacen
        fields = [
            'id', 'nombre', 'sigla', 'ubicacion', 'activo',
            'subalmacenes_count', 'creado_por', 'fecha_creacion'
        ]
        read_only_fields = ['creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion']

class SubAlmacenSerializer(serializers.ModelSerializer):
    almacen_nombre = serializers.CharField(source='almacen.nombre', read_only=True)
    almacen_sigla = serializers.CharField(source='almacen.sigla', read_only=True)
    
    class Meta:
        model = SubAlmacen
        fields = [
            'id', 'almacen', 'almacen_nombre', 'almacen_sigla',
            'nombre', 'sigla', 'ubicacion', 'activo',
            'creado_por', 'fecha_creacion'
        ]
        read_only_fields = ['creado_por', 'fecha_creacion', 'modificado_por', 'fecha_modificacion']