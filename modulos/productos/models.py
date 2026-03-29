from django.db import models
from modulos.utilitario.models import AuditoriaBase
from modulos.almacenes.models import SubAlmacen 

class UnidadMedida(models.Model):
    """Unidades de medida (ej: UN, KG, LT)"""
    codigo = models.CharField("Código", max_length=10, unique=True)
    nombre = models.CharField("Nombre", max_length=50)
    abreviatura = models.CharField("Abreviatura", max_length=10)
    
    class Meta:
        verbose_name = "Unidad de Medida"
        verbose_name_plural = "Unidades de Medida"
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} ({self.abreviatura})"

class CategoriaProducto(models.Model):
    """Categorías de productos"""
    nombre = models.CharField("Nombre", max_length=100, unique=True)
    descripcion = models.TextField("Descripción", blank=True, null=True)
    
    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

class Producto(AuditoriaBase):
    """Productos del sistema"""
    codigo = models.CharField("Código", max_length=50, unique=True)
    nombre = models.CharField("Nombre", max_length=200)
    descripcion = models.TextField("Descripción", blank=True, null=True)
    
    unidad_medida = models.ForeignKey(
        UnidadMedida, 
        on_delete=models.PROTECT,
        verbose_name="Unidad de Medida",
        related_name='productos'
    )
    categoria = models.ForeignKey(
        CategoriaProducto,
        on_delete=models.PROTECT,
        verbose_name="Categoría",
        related_name='productos'
    )
    
    stock_minimo = models.DecimalField("Stock mínimo", max_digits=10, decimal_places=2, default=0)
    stock_maximo = models.DecimalField("Stock máximo", max_digits=10, decimal_places=2, default=0)
    
    imagen = models.ImageField("Imagen", upload_to='productos/', null=True, blank=True)
    activo = models.BooleanField("Activo", default=True)
    
    # Un producto puede estar en múltiples subalmacenes (a través de StockProducto)
    subalmacenes = models.ManyToManyField(
        SubAlmacen,
        through='StockProducto',
        related_name='productos'
    )
    
    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['nombre']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    @property
    def stock_total(self):
        """Calcula el stock total en todos los subalmacenes"""
        return sum(stock.cantidad for stock in self.stocks.all())

class StockProducto(models.Model):
    """Stock de un producto en un subalmacén específico"""
    producto = models.ForeignKey(
        Producto, 
        on_delete=models.CASCADE,
        related_name='stocks'
    )
    subalmacen = models.ForeignKey(
        SubAlmacen,
        on_delete=models.CASCADE,
        related_name='stocks'
    )
    cantidad = models.DecimalField("Cantidad actual", max_digits=10, decimal_places=2, default=0)
    ubicacion = models.CharField("Ubicación específica", max_length=100, blank=True, null=True)
    
    # Control de movimientos
    fecha_ultimo_ingreso = models.DateTimeField("Último ingreso", null=True, blank=True)
    fecha_ultimo_egreso = models.DateTimeField("Último egreso", null=True, blank=True)
    
    class Meta:
        verbose_name = "Stock de Producto"
        verbose_name_plural = "Stocks de Productos"
        unique_together = ['producto', 'subalmacen']
        indexes = [
            models.Index(fields=['producto', 'subalmacen']),
        ]
    
    def __str__(self):
        return f"{self.producto.nombre} en {self.subalmacen.nombre}: {self.cantidad}"

class MovimientoStock(models.Model):
    """Registro de todos los movimientos de stock (trazabilidad)"""
    TIPO_CHOICES = [
        ('INGRESO', 'Ingreso'),
        ('EGRESO', 'Egreso'),
        ('AJUSTE', 'Ajuste'),
    ]
    
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name='movimientos'
    )
    subalmacen = models.ForeignKey(
        SubAlmacen,
        on_delete=models.PROTECT,
        related_name='movimientos'
    )
    tipo = models.CharField("Tipo", max_length=10, choices=TIPO_CHOICES, blank=True, null=True)
    cantidad = models.DecimalField("Cantidad", max_digits=10, decimal_places=2, blank=True, null=True)
    stock_anterior = models.DecimalField("Stock anterior", max_digits=10, decimal_places=2, blank=True, null=True)
    stock_nuevo = models.DecimalField("Stock nuevo", max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Referencia al origen del movimiento
    ingreso = models.ForeignKey(
        'ingresos.Ingreso',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movimientos_stock'
    )
    
    observacion = models.TextField("Observación", blank=True, null=True)
    fecha_movimiento = models.DateTimeField("Fecha del movimiento", auto_now_add=True)
    creado_por = models.ForeignKey(
        'users.Usuario',
        on_delete=models.PROTECT,
        related_name='movimientos_stock'
    )
    
    class Meta:
        verbose_name = "Movimiento de Stock"
        verbose_name_plural = "Movimientos de Stock"
        ordering = ['-fecha_movimiento']
    
    def __str__(self):
        return f"{self.tipo} - {self.producto.nombre}: {self.cantidad}"