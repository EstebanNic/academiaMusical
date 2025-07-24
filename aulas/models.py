from django.db import models

# Create your models here.

class Sede(models.TextChoices):
    MATRIZ = 'MATRIZ', 'Sede Matriz'
    NORTE = 'NORTE', 'Sede Norte'

class Edificio(models.TextChoices):
    NUEVO = 'NUEVO', 'Edificio Nuevo'
    VIEJO = 'VIEJO', 'Edificio Viejo'

class Piso(models.TextChoices):
    PISO_1 = '1', 'Piso 1'
    PISO_2 = '2', 'Piso 2'
    PISO_3 = '3', 'Piso 3'

class Aula(models.Model):
    nombre = models.CharField(max_length=50, unique=True, help_text="Nombre del aula (ej: Aula 101)")
    sede = models.CharField(max_length=10, choices=Sede.choices, default=Sede.MATRIZ)
    edificio = models.CharField(max_length=10, choices=Edificio.choices, default=Edificio.NUEVO)
    piso = models.CharField(max_length=2, choices=Piso.choices, default=Piso.PISO_1)
    capacidad = models.PositiveIntegerField(default=15, help_text="Capacidad máxima de estudiantes")
    activa = models.BooleanField(default=True, help_text="Indica si el aula está disponible para uso")

    class Meta:
        ordering = ['sede', 'edificio', 'piso', 'nombre']
        verbose_name = 'Aula'
        verbose_name_plural = 'Aulas'

    def __str__(self):
        return f"{self.nombre} - {self.get_sede_display()}, {self.get_edificio_display()}, {self.get_piso_display()}"

    @property
    def ubicacion_completa(self):
        return f"{self.get_sede_display()} - {self.get_edificio_display()} - {self.get_piso_display()}"
