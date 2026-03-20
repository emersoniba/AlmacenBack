from django.db import models
from modulos.utilitario.models import AuditoriaBase
from modulos.almacenes.models import SubAlmacen 

class UnidadMedida(models.Model):
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
    nombre = models.CharField("Nombre", max_length=100, unique=True)
    descripcion = models.TextField("Descripción", blank=True, null=True)
    
    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

class Producto(AuditoriaBase):
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
    
    # Un producto puede estar en múltiples subalmacenes
    subalmacenes = models.ManyToManyField(
        SubAlmacen,
        through='StockProducto',
        related_name='productos'
    )
    
    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

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
    fecha_ultimo_movimiento = models.DateTimeField("Último movimiento", auto_now=True)
    
    class Meta:
        verbose_name = "Stock de Producto"
        verbose_name_plural = "Stocks de Productos"
        unique_together = ['producto', 'subalmacen']
    
    def __str__(self):
        return f"{self.producto.nombre} en {self.subalmacen.nombre}: {self.cantidad}"