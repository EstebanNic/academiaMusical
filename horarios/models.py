from django.db import models
from cursos.models import Curso
from usuarios.models import Usuario

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
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    descripcion = models.TextField(blank=True)

    @property
    def codigo(self):
        return f"{self.curso.nombre[:3].upper()}-{self.id:04d}"

    def __str__(self):
        return f"{self.curso.nombre} - {self.fecha_inicio} a {self.fecha_fin} {self.hora_inicio}-{self.hora_fin}"
