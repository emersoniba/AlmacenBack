from django.db import models
from django.core.validators import MinValueValidator
from modulos.utilitario.models import AuditoriaBase
from modulos.users.models import Usuario
from modulos.almacenes.models import Almacen, SubAlmacen
from modulos.productos.models import Producto

class EstadoSolicitud(models.Model):
    """Tabla de estados de solicitud (sin choices)"""
    nombre = models.CharField("Nombre del estado", max_length=50, unique=True)
    codigo = models.CharField("Código", max_length=20, unique=True)
    descripcion = models.TextField("Descripción", blank=True, null=True)
    orden = models.IntegerField("Orden", default=0)
    
    class Meta:
        verbose_name = "Estado de Solicitud"
        verbose_name_plural = "Estados de Solicitud"
        ordering = ['orden']
    
    def __str__(self):
        return self.nombre

class Solicitud(AuditoriaBase):
    """Solicitud de materiales"""
    codigo = models.CharField("Código", max_length=50, unique=True)
    objetivo = models.TextField("Objetivo de la solicitud")
    
    # Relaciones
    solicitante = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='solicitudes_realizadas',
        verbose_name="Solicitante"
    )
    aprobador = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='solicitudes_aprobadas',
        verbose_name="Aprobador"
    )
    almacenero = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='solicitudes_atendidas',
        verbose_name="Almacenero"
    )
    almacen = models.ForeignKey(
        Almacen,
        on_delete=models.PROTECT,
        related_name='solicitudes',
        verbose_name="Almacén"
    )
    subalmacen = models.ForeignKey(
        SubAlmacen,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='solicitudes',
        verbose_name="Subalmacén"
    )
    
    # Fechas del flujo
    fecha_solicitud = models.DateTimeField("Fecha de solicitud", auto_now_add=True)
    fecha_envio = models.DateTimeField("Fecha de envío", null=True, blank=True)
    fecha_aprobacion = models.DateTimeField("Fecha de aprobación", null=True, blank=True)
    fecha_rechazo = models.DateTimeField("Fecha de rechazo", null=True, blank=True)
    fecha_recepcion = models.DateTimeField("Fecha de recepción", null=True, blank=True)
    
    # Estado
    estado = models.ForeignKey(
        EstadoSolicitud,
        on_delete=models.PROTECT,
        related_name='solicitudes',
        verbose_name="Estado"
    )
    
    # Observaciones
    observacion_aprobador = models.TextField("Observación del aprobador", blank=True, null=True)
    observacion_almacenero = models.TextField("Observación del almacenero", blank=True, null=True)
    
    class Meta:
        verbose_name = "Solicitud"
        verbose_name_plural = "Solicitudes"
        ordering = ['-fecha_solicitud']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['solicitante', 'estado']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.solicitante.username}"

class DetalleSolicitud(models.Model):
    """Detalle de productos solicitados"""
    solicitud = models.ForeignKey(
        Solicitud,
        on_delete=models.CASCADE,
        related_name='detalles'
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        verbose_name="Producto"
    )
    cantidad_solicitada = models.DecimalField(
        "Cantidad solicitada",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    cantidad_entregada = models.DecimalField(
        "Cantidad entregada",
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    class Meta:
        verbose_name = "Detalle de Solicitud"
        verbose_name_plural = "Detalles de Solicitud"
        unique_together = ['solicitud', 'producto']
    
    def __str__(self):
        return f"{self.producto.nombre} - {self.cantidad_solicitada}"

class HistorialSolicitud(models.Model):
    """Historial de cambios de estado de la solicitud"""
    solicitud = models.ForeignKey(
        Solicitud,
        on_delete=models.CASCADE,
        related_name='historial'
    )
    estado_anterior = models.ForeignKey(
        EstadoSolicitud,
        on_delete=models.PROTECT,
        related_name='+',
        verbose_name="Estado anterior",null=True, 
        blank=True
    )
    estado_nuevo = models.ForeignKey(
        EstadoSolicitud,
        on_delete=models.PROTECT,
        related_name='+',
        verbose_name="Estado nuevo"
    )
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        verbose_name="Usuario que realizó el cambio"
    )
    observacion = models.TextField("Observación", blank=True, null=True)
    fecha_cambio = models.DateTimeField("Fecha de cambio", auto_now_add=True)
    
    class Meta:
        verbose_name = "Historial de Solicitud"
        verbose_name_plural = "Historiales de Solicitudes"
        ordering = ['-fecha_cambio']
    
    def __str__(self):
        return f"{self.solicitud.codigo}: {self.estado_anterior.nombre} -> {self.estado_nuevo.nombre}"