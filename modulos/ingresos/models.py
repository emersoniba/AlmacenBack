from django.db import models
from modulos.utilitario.models import AuditoriaBase
from modulos.proveedores.models import Proveedor
from modulos.almacenes.models import Almacen, SubAlmacen
from modulos.productos.models import Producto

class EstadoIngreso(models.Model):
    """Tabla para estados de ingreso (sin choices)"""
    nombre = models.CharField("Nombre del estado", max_length=50, unique=True)
    codigo = models.CharField("Código", max_length=20, unique=True)
    descripcion = models.TextField("Descripción", blank=True, null=True)
    orden = models.IntegerField("Orden", default=0)
    
    class Meta:
        verbose_name = "Estado de Ingreso"
        verbose_name_plural = "Estados de Ingreso"
        ordering = ['orden', 'nombre']
    
    def __str__(self):
        return self.nombre

class Ingreso(AuditoriaBase):
    codigo = models.CharField("Código", max_length=50, unique=True)
    descripcion = models.TextField("Descripción")
    comprobante = models.CharField("N° Comprobante", max_length=100)
    fecha_ingreso = models.DateTimeField("Fecha de ingreso")
    
    proveedor = models.ForeignKey(
        Proveedor, 
        on_delete=models.PROTECT,
        related_name='ingresos',
        verbose_name="Proveedor"
    )
    almacen = models.ForeignKey(
        Almacen,
        on_delete=models.PROTECT,
        related_name='ingresos',
        verbose_name="Almacén"
    )
    subalmacen = models.ForeignKey(
        SubAlmacen,
        on_delete=models.PROTECT,
        related_name='ingresos',
        verbose_name="Subalmacén",
        null=True,
        blank=True
    )
    
    gestion = models.IntegerField("Gestión")
    
    # Relación con estado (reemplaza choices)
    estado = models.ForeignKey(
        EstadoIngreso,
        on_delete=models.PROTECT,
        related_name='ingresos',
        verbose_name="Estado",
        null=True,
        blank=True
    )
    
    observacion_anulacion = models.TextField("Observación de anulación", blank=True, null=True)
    fecha_anulacion = models.DateTimeField("Fecha de anulación", null=True, blank=True)
    
    class Meta:
        verbose_name = "Ingreso"
        verbose_name_plural = "Ingresos"
        ordering = ['-fecha_ingreso']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['gestion', 'estado']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.fecha_ingreso.strftime('%d/%m/%Y')}"

class IngresoDetalle(models.Model):
    ingreso = models.ForeignKey(
        Ingreso, 
        on_delete=models.CASCADE,
        related_name='detalles'
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        verbose_name="Producto",
        related_name='ingresos_detalle'
    )
    cantidad = models.DecimalField("Cantidad", max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField("Precio Unitario", max_digits=10, decimal_places=2)
    
    # Control de stock
    stock_actualizado = models.BooleanField("Stock actualizado", default=False)
    fecha_actualizacion_stock = models.DateTimeField("Fecha actualización stock", null=True, blank=True)
    
    class Meta:
        verbose_name = "Detalle de Ingreso"
        verbose_name_plural = "Detalles de Ingreso"
        indexes = [
            models.Index(fields=['ingreso', 'producto']),
        ]
    
    @property
    def subtotal(self) -> float:
        return float(self.cantidad) * float(self.precio_unitario)
    
    def __str__(self):
        return f"{self.producto.nombre} - {self.cantidad}"