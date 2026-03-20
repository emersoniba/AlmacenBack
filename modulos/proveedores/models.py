from django.db import models
from modulos.utilitario.models import AuditoriaBase


class Proveedor(AuditoriaBase):
    razon_social = models.CharField("Razón Social", max_length=255)
    nit = models.CharField("NIT", max_length=50, unique=True)
    direccion = models.TextField("Dirección", blank=True, null=True)
    telefono = models.CharField("Teléfono", max_length=50, blank=True, null=True)
    email = models.EmailField("Email", blank=True, null=True)
    contacto = models.CharField(
        "Persona de contacto", max_length=200, blank=True, null=True
    )
    activo = models.BooleanField("Activo", default=True)

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ["razon_social"]

    def __str__(self):
        return f"{self.razon_social} - {self.nit}"

    def eliminar_logico(self, user):
        """Método para realizar eliminado lógico"""
        self.activo = False
        self.eliminado_por = user
        self.fecha_eliminacion = models.DateTimeField(
            auto_now=True
        )  # Se actualizará automáticamente
        self.save()
