# matriculas/models.py

from django.db import models
from usuarios.models import Usuario
from horarios.models import Horario

class EstadoMatricula(models.TextChoices):
    ACTIVA = 'ACTIVA', 'Activa'
    FINALIZADA = 'FINALIZADA', 'Finalizada'
    CANCELADA = 'CANCELADA', 'Cancelada'

class Matricula(models.Model):
    estudiante = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        limit_choices_to={'rol': Usuario.Rol.ESTUDIANTE},
        related_name='matriculas'
    )
    clase = models.ForeignKey(
        Horario,
        on_delete=models.CASCADE,
        related_name='matriculas'
    )
    fecha_matricula = models.DateField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=EstadoMatricula.choices, default=EstadoMatricula.ACTIVA)
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('estudiante', 'clase')  # No se permite duplicar una matrícula estudiante-clase

    def __str__(self):
        return f"{self.estudiante.get_full_name()} - {self.clase.curso.nombre}"
