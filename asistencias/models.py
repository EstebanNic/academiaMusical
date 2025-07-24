from django.db import models
from matriculas.models import Matricula
from horarios.models import Horario

class EstadoAsistencia(models.TextChoices):
    PRESENTE = 'PRESENTE', 'Presente'
    TARDE = 'TARDE', 'Llegó tarde'
    AUSENTE = 'AUSENTE', 'Ausente'
    JUSTIFICADO = 'JUSTIFICADO', 'Ausencia justificada'

class Asistencia(models.Model):
    matricula = models.ForeignKey(Matricula, on_delete=models.CASCADE, related_name='asistencias')
    clase = models.ForeignKey(Horario, on_delete=models.CASCADE, related_name='asistencias')
    fecha = models.DateField()
    estado = models.CharField(
        max_length=12,
        choices=EstadoAsistencia.choices,
        default=EstadoAsistencia.AUSENTE
    )
    observaciones = models.TextField(blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('matricula', 'fecha')
        ordering = ['-fecha', 'matricula__estudiante__first_name']

    def __str__(self):
        return f"{self.matricula.estudiante.get_full_name()} - {self.fecha} - {self.estado}"

    @property
    def estudiante(self):
        return self.matricula.estudiante

    @property
    def curso(self):
        return self.matricula.clase.curso
