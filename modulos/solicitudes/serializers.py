from rest_framework import serializers
from .models import EstadoSolicitud, Solicitud, DetalleSolicitud, HistorialSolicitud
from modulos.users.serializers import UsuarioSerializer
from modulos.productos.serializers import ProductoSerializer
from modulos.productos.models import StockProducto


class EstadoSolicitudSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoSolicitud
        fields = ["id", "nombre", "codigo", "descripcion", "orden"]


class DetalleSolicitudSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source="producto.nombre", read_only=True)
    producto_codigo = serializers.CharField(source="producto.codigo", read_only=True)
    producto_unidad = serializers.CharField(
        source="producto.unidad_medida.abreviatura", read_only=True
    )
    stock_actual = serializers.SerializerMethodField()

    class Meta:
        model = DetalleSolicitud
        fields = [
            "id",
            "producto",
            "producto_nombre",
            "producto_codigo",
            "producto_unidad",
            "cantidad_solicitada",
            "cantidad_entregada",
            "stock_actual",
        ]

    def get_stock_actual(self, obj):
        """Obtener stock actual del producto en el subalmacén de la solicitud"""
        try:
            # Obtener la solicitud asociada al detalle
            solicitud = obj.solicitud

            # Si la solicitud tiene subalmacén, buscar el stock en ese subalmacén
            if solicitud.subalmacen:
                stock = StockProducto.objects.filter(
                    producto=obj.producto, subalmacen=solicitud.subalmacen
                ).first()

                if stock:
                    return float(stock.cantidad)
                else:
                    # Si no hay registro de stock en ese subalmacén, el stock es 0
                    return 0
            else:
                # Si no hay subalmacén, sumar stock de todos los subalmacenes
                # O usar el stock total del producto
                return float(obj.producto.stock_total)

        except Exception as e:
            print(f"Error al obtener stock: {e}")
            return 0


class SolicitudListSerializer(serializers.ModelSerializer):
    """Serializer para listar solicitudes (sin detalles)"""

    solicitante_nombre = serializers.CharField(
        source="solicitante.username", read_only=True
    )
    solicitante_cargo = serializers.CharField(
        source="solicitante.persona.cargo", read_only=True
    )
    aprobador_nombre = serializers.CharField(
        source="aprobador.username", read_only=True, default=None
    )
    almacenero_nombre = serializers.CharField(
        source="almacenero.username", read_only=True, default=None
    )
    almacen_nombre = serializers.CharField(source="almacen.nombre", read_only=True)
    subalmacen_nombre = serializers.CharField(
        source="subalmacen.nombre", read_only=True
    )
    estado_nombre = serializers.CharField(source="estado.nombre", read_only=True)
    estado_codigo = serializers.CharField(source="estado.codigo", read_only=True)
    estado_descripcion = serializers.CharField(
        source="estado.descripcion", read_only=True
    )

    class Meta:
        model = Solicitud
        fields = [
            "id",
            "codigo",
            "objetivo",
            "solicitante",
            "solicitante_nombre",
            "solicitante_cargo",
            "aprobador",
            "aprobador_nombre",
            "almacenero",
            "almacenero_nombre",
            "almacen",
            "almacen_nombre",
            "subalmacen",
            "subalmacen_nombre",
            "fecha_solicitud",
            "fecha_envio",
            "fecha_aprobacion",
            "fecha_rechazo",
            "fecha_recepcion",
            "estado",
            "estado_nombre",
            "estado_codigo",
            "estado_descripcion",
            "observacion_aprobador",
            "observacion_almacenero",
        ]
        read_only_fields = [
            "codigo",
            "fecha_solicitud",
            "fecha_envio",
            "fecha_aprobacion",
            "fecha_rechazo",
            "fecha_recepcion",
        ]

    def get_solicitante_nombre(self, obj):
        """Obtener nombre completo del solicitante"""
        if obj.solicitante and obj.solicitante.persona:
            persona = obj.solicitante.persona
            nombre_completo = f"{persona.nombres} {persona.apellido_paterno or ''} {persona.apellido_materno or ''}".strip()
            return nombre_completo or obj.solicitante.username
        return obj.solicitante.username if obj.solicitante else None

    def get_solicitante_cargo(self, obj):
        """Obtener cargo del solicitante"""
        if obj.solicitante and obj.solicitante.persona:
            return obj.solicitante.persona.cargo
        return None

    def get_aprobador_nombre(self, obj):
        """Obtener nombre del aprobador"""
        if obj.aprobador and obj.aprobador.persona:
            persona = obj.aprobador.persona
            nombre_completo = f"{persona.nombres} {persona.apellido_paterno or ''} {persona.apellido_materno or ''}".strip()
            return nombre_completo or obj.aprobador.username
        return obj.aprobador.username if obj.aprobador else None

    def get_almacenero_nombre(self, obj):
        """Obtener nombre del almacenero"""
        if obj.almacenero and obj.almacenero.persona:
            persona = obj.almacenero.persona
            nombre_completo = f"{persona.nombres} {persona.apellido_paterno or ''} {persona.apellido_materno or ''}".strip()
            return nombre_completo or obj.almacenero.username
        return obj.almacenero.username if obj.almacenero else None


class SolicitudDetailSerializer(serializers.ModelSerializer):
    """Serializer para detalle de solicitud (con detalles)"""

    solicitante = UsuarioSerializer(read_only=True)
    aprobador = UsuarioSerializer(read_only=True)
    almacenero = UsuarioSerializer(read_only=True)
    almacen_nombre = serializers.CharField(source="almacen.nombre", read_only=True)
    subalmacen_nombre = serializers.CharField(
        source="subalmacen.nombre", read_only=True
    )
    estado_nombre = serializers.CharField(source="estado.nombre", read_only=True)
    estado_codigo = serializers.CharField(source="estado.codigo", read_only=True)
    detalles = DetalleSolicitudSerializer(many=True, read_only=True)

    class Meta:
        model = Solicitud
        fields = "__all__"

    def get_solicitante(self, obj):
        """Obtener datos completos del solicitante"""
        if obj.solicitante:
            data = {
                "id": obj.solicitante.id,
                "username": obj.solicitante.username,
            }
            if obj.solicitante.persona:
                persona = obj.solicitante.persona
                data["nombre_completo"] = (
                    f"{persona.nombres} {persona.apellido_paterno or ''} {persona.apellido_materno or ''}".strip()
                )
                data["cargo"] = persona.cargo
                data["unidad"] = persona.unidad
            else:
                data["nombre_completo"] = obj.solicitante.username
                data["cargo"] = None
                data["unidad"] = None
            return data
        return None

    def get_aprobador(self, obj):
        """Obtener datos del aprobador"""
        if obj.aprobador:
            data = {
                "id": obj.aprobador.id,
                "username": obj.aprobador.username,
            }
            if obj.aprobador.persona:
                persona = obj.aprobador.persona
                data["nombre_completo"] = (
                    f"{persona.nombres} {persona.apellido_paterno or ''} {persona.apellido_materno or ''}".strip()
                )
            else:
                data["nombre_completo"] = obj.aprobador.username
            return data
        return None

    def get_almacenero(self, obj):
        """Obtener datos del almacenero"""
        if obj.almacenero:
            data = {
                "id": obj.almacenero.id,
                "username": obj.almacenero.username,
            }
            if obj.almacenero.persona:
                persona = obj.almacenero.persona
                data["nombre_completo"] = (
                    f"{persona.nombres} {persona.apellido_paterno or ''} {persona.apellido_materno or ''}".strip()
                )
            else:
                data["nombre_completo"] = obj.almacenero.username
            return data
        return None


class DetalleSolicitudCreateSerializer(serializers.Serializer):
    """Serializer para crear detalles de solicitud"""

    producto = serializers.IntegerField()
    cantidad_solicitada = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=0.01
    )


class SolicitudCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear solicitud"""

    detalles = DetalleSolicitudCreateSerializer(many=True, write_only=True)

    class Meta:
        model = Solicitud
        fields = ["objetivo", "almacen", "subalmacen", "detalles"]

    def validate_detalles(self, value):
        if not value:
            raise serializers.ValidationError("Debe incluir al menos un producto")

        # Validar que los productos existan y tengan stock
        from modulos.productos.models import Producto, StockProducto

        for detalle in value:
            producto_id = detalle.get("producto")
            cantidad = detalle.get("cantidad_solicitada")

            try:
                producto = Producto.objects.get(id=producto_id, activo=True)
            except Producto.DoesNotExist:
                raise serializers.ValidationError(
                    f"Producto con ID {producto_id} no existe o está inactivo"
                )

            # Verificar stock en el subalmacén seleccionado
            subalmacen_id = self.initial_data.get("subalmacen")
            if subalmacen_id:
                stock = StockProducto.objects.filter(
                    producto=producto, subalmacen_id=subalmacen_id
                ).first()

                if not stock or stock.cantidad < cantidad:
                    raise serializers.ValidationError(
                        f"Stock insuficiente para {producto.nombre}. "
                        f"Stock disponible: {stock.cantidad if stock else 0}, "
                        f"Solicitado: {cantidad}"
                    )

        return value

    def create(self, validated_data):
        from django.utils import timezone
        from .models import EstadoSolicitud

        detalles_data = validated_data.pop("detalles")
        request = self.context.get("request")

        # Generar código automático
        gestion = timezone.now().year
        ultima_solicitud = (
            Solicitud.objects.filter(fecha_solicitud__year=gestion)
            .order_by("-id")
            .first()
        )

        if ultima_solicitud:
            try:
                ultimo_numero = int(ultima_solicitud.codigo.split("-")[-1])
                nuevo_numero = ultimo_numero + 1
            except (ValueError, IndexError):
                nuevo_numero = 1
        else:
            nuevo_numero = 1

        codigo = f"SOL-{gestion}-{nuevo_numero:04d}"

        # Obtener estado PENDIENTE
        estado_pendiente = EstadoSolicitud.objects.filter(codigo="PENDIENTE").first()
        if not estado_pendiente:
            # Crear estado pendiente si no existe
            estado_pendiente = EstadoSolicitud.objects.create(
                nombre="Pendiente",
                codigo="PENDIENTE",
                descripcion="Solicitud pendiente de envío",
                orden=1,
            )

        # Crear solicitud
        solicitud = Solicitud.objects.create(
            **validated_data,
            codigo=codigo,
            solicitante=request.user if request else None,
            estado=estado_pendiente,
            fecha_solicitud=timezone.now(),
            creado_por=request.user if request else None,  # Asignar creado_por
            fecha_creacion=timezone.now(),
        )

        # Crear detalles
        for detalle_data in detalles_data:
            DetalleSolicitud.objects.create(
                solicitud=solicitud,
                producto_id=detalle_data["producto"],
                cantidad_solicitada=detalle_data["cantidad_solicitada"],
                cantidad_entregada=0,
            )

        # Registrar historial
        HistorialSolicitud.objects.create(
            solicitud=solicitud,
            estado_anterior=None,
            estado_nuevo=estado_pendiente,
            usuario=request.user if request else None,
            observacion="Solicitud creada",
        )

        return solicitud


class SolicitudAprobarSerializer(serializers.Serializer):
    """Serializer para aprobar solicitud"""

    aprobar = serializers.BooleanField(required=True)
    observacion = serializers.CharField(required=False, allow_blank=True)


class SolicitudEntregarSerializer(serializers.Serializer):
    """Serializer para entregar productos"""

    entregas = serializers.ListField(child=serializers.DictField(), required=True)
    observacion = serializers.CharField(required=False, allow_blank=True)
