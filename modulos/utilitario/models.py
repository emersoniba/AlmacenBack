from django.db import models
from django.conf import settings


class AuditoriaBase(models.Model):
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='+')
    eliminado_por = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT,
                                      related_name='+')
    modificado_por = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT,
                                       related_name='+')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(null=True, blank=True)
    fecha_eliminacion = models.DateTimeField(null=True, blank=True)
    accion = models.JSONField(null=True, blank=True)

    class Meta:
        abstract = True


class Feriado(models.Model):
    fecha = models.DateField(unique=True)
    descripcion = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.fecha} - {self.descripcion}"