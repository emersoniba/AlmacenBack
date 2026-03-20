from django.db import models
from modulos.utilitario.models import AuditoriaBase
from modulos.almacenes.models import Almacen
from modulos.users.models import Usuario

class ResponsableAlmacen(AuditoriaBase):
    almacen = models.ForeignKey(
        Almacen,
        on_delete=models.PROTECT,
        related_name='responsables',
        verbose_name="Almacén"
    )
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='responsabilidades',
        verbose_name="Usuario responsable"
    )
    fecha_desde = models.DateField("Fecha desde")
    fecha_hasta = models.DateField("Fecha hasta", null=True, blank=True)
    activo = models.BooleanField("Activo", default=True)
    
    class Meta:
        verbose_name = "Responsable de Almacén"
        verbose_name_plural = "Responsables de Almacén"
        ordering = ['-fecha_desde']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.almacen.nombre}"