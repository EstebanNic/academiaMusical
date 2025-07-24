from django.db import models
from cursos.models import Curso
from usuarios.models import Usuario
from aulas.models import Aula

class Horario(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='clases')
    profesor = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'rol': Usuario.Rol.PROFESOR},
        related_name='clases_profesor'
    )
    aula = models.ForeignKey(
        Aula,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clases_aula'
    )
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    descripcion = models.TextField(blank=True)
    cupos = models.PositiveIntegerField(default=15, help_text="Cupos máximos para la clase")

    @property
    def codigo(self):
        return f"{self.curso.nombre[:3].upper()}-{self.id:04d}"

    def __str__(self):
        aula_info = f" - {self.aula.nombre}" if self.aula else ""
        return f"{self.curso.nombre} - {self.fecha_inicio} a {self.fecha_fin} {self.hora_inicio}-{self.hora_fin}{aula_info}"
