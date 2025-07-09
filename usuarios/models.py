from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    class Rol(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrador'
        PROFESOR = 'PROFESOR', 'Profesor'
        ESTUDIANTE = 'ESTUDIANTE', 'Estudiante'

    rol = models.CharField(max_length=10, choices=Rol.choices, default=Rol.ESTUDIANTE)

    # Campos adicionales
    cedula = models.CharField(max_length=20, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    instrumento = models.CharField(max_length=100, blank=True, null=True)  # <--- NUEVO CAMPO

    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"

