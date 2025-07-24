from django.db import models
from matriculas.models import Matricula

class EstadoPago(models.TextChoices):
    PENDIENTE = 'PENDIENTE', 'Pendiente'
    PAGADO = 'PAGADO', 'Pagado'
    CANCELADO = 'CANCELADO', 'Cancelado'

class Pago(models.Model):
    matricula = models.ForeignKey(Matricula, on_delete=models.CASCADE, related_name='pagos')
    monto = models.DecimalField(max_digits=8, decimal_places=2)
    fecha_pago = models.DateField(auto_now_add=True)
    estado = models.CharField(max_length=10, choices=EstadoPago.choices, default=EstadoPago.PENDIENTE)
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Pago de {self.matricula.estudiante.get_full_name()} - {self.monto} ({self.get_estado_display()})"
