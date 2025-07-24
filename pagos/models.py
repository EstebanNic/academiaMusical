from django.db import models
from matriculas.models import Matricula

class EstadoPago(models.TextChoices):
    PENDIENTE = 'PENDIENTE', 'Pendiente'
    PAGADO = 'PAGADO', 'Pagado'
    CANCELADO = 'CANCELADO', 'Cancelado'

class Pago(models.Model):
    matricula = models.ForeignKey(Matricula, on_delete=models.CASCADE, related_name='pagos')
    monto = models.DecimalField(max_digits=8, decimal_places=2, help_text="Monto total a pagar")
    fecha_pago = models.DateField(auto_now_add=True)
    estado = models.CharField(max_length=10, choices=EstadoPago.choices, default=EstadoPago.PENDIENTE)
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Pago de {self.matricula.estudiante.get_full_name()} - {self.monto} ({self.get_estado_display()})"

    @property
    def saldo_pendiente(self):
        pagado = sum([float(p.monto) for p in self.pagos_parciales.all()])
        return float(self.monto) - pagado

    def actualizar_estado(self):
        if self.saldo_pendiente <= 0:
            self.estado = EstadoPago.PAGADO
        else:
            self.estado = EstadoPago.PENDIENTE
        self.save()

class PagoParcial(models.Model):
    pago = models.ForeignKey(Pago, on_delete=models.CASCADE, related_name='pagos_parciales')
    monto = models.DecimalField(max_digits=8, decimal_places=2)
    fecha = models.DateField(auto_now_add=True)
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Abono de ${self.monto} ({self.fecha})"
