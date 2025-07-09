# profesores/models.py
from django.db import models
from usuarios.models import Usuario

class Profesor(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.usuario)
