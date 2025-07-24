from django.db import models
from usuarios.models import Usuario

class Nivel(models.TextChoices):
    PRINCIPIANTE = 'PRINCIPIANTE', 'Principiante'
    INTERMEDIO = 'INTERMEDIO', 'Intermedio'
    AVANZADO = 'AVANZADO', 'Avanzado'

class Curso(models.Model):
    nombre = models.CharField(max_length=100)
    nivel = models.CharField(max_length=20, choices=Nivel.choices, default=Nivel.PRINCIPIANTE)
    instrumento = models.CharField(max_length=100)
    profesor = models.ForeignKey(
        Usuario, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        limit_choices_to={'rol': Usuario.Rol.PROFESOR},
        related_name='cursos_profesor'
    )
    precio = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, help_text="Precio del curso")

    # Opcional: descripción
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} - {self.instrumento} ({self.get_nivel_display()})"
