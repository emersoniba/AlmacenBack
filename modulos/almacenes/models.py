from django.db import models
from modulos.utilitario.models import AuditoriaBase

class Almacen(AuditoriaBase):
    nombre = models.CharField("Nombre del almacén", max_length=200)
    sigla = models.CharField("Sigla", max_length=20, unique=True)
    ubicacion = models.TextField("Ubicación", blank=True, null=True)
    activo = models.BooleanField("Activo", default=True)
    
    class Meta:
        verbose_name = "Almacén"
        verbose_name_plural = "Almacenes"
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} ({self.sigla})"

class SubAlmacen(AuditoriaBase):
    almacen = models.ForeignKey( Almacen, on_delete=models.PROTECT,related_name='subalmacenes',verbose_name="Almacén principal")
    nombre = models.CharField("Nombre del subalmacén", max_length=200)
    sigla = models.CharField("Sigla", max_length=20)
    ubicacion = models.TextField("Ubicación", blank=True, null=True)
    activo = models.BooleanField("Activo", default=True)
    
    class Meta:
        verbose_name = "Subalmacén"
        verbose_name_plural = "Subalmacenes"
        ordering = ['nombre']
        unique_together = ['almacen', 'sigla']
    
    def __str__(self):
        return f"{self.almacen.sigla} - {self.nombre} ({self.sigla})"