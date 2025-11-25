from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

# 1) Modelo EspacioParqueadero
class EspacioParqueadero(models.Model):
    TIPO_CHOICES = [
        ('CARRO', 'CARRO'),
        ('MOTO', 'MOTO'),
        ('DISCAPACIDAD', 'DISCAPACIDAD'),
    ]
    ESTADO_CHOICES = [
        ('LIBRE', 'LIBRE'),
        ('RESERVADO', 'RESERVADO'),
        ('OCUPADO', 'OCUPADO'),
        ('BLOQUEADO', 'BLOQUEADO'),
    ]

    numero = models.IntegerField(unique=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='LIBRE')

    def __str__(self):
        return f"Espacio {self.numero} - {self.tipo} - {self.estado}"

# 2) Modelo Reserva
class Reserva(models.Model):
    TIPO_VEHICULO_CHOICES = [
        ('CARRO', 'CARRO'),
        ('MOTO', 'MOTO'),
    ]
    ESTADO_CHOICES = [
        ('RESERVADA', 'RESERVADA'),
        ('CANCELADA', 'CANCELADA'),
        ('COMPLETADA', 'COMPLETADA'),
        ('VENCIDA', 'VENCIDA'),
    ]

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reservas')
    espacio = models.ForeignKey(EspacioParqueadero, on_delete=models.PROTECT, related_name='reservas')
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    tipo_vehiculo = models.CharField(max_length=10, choices=TIPO_VEHICULO_CHOICES)
    placa = models.CharField(max_length=20)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='RESERVADA')
    
    # Campos de auditoría operativa
    hora_entrada = models.TimeField(null=True, blank=True)
    hora_salida = models.TimeField(null=True, blank=True)
    
    # Timestamps
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def clean(self):
        # Validación básica: hora_inicio debe ser menor que hora_fin
        if self.hora_inicio and self.hora_fin and self.hora_inicio >= self.hora_fin:
            raise ValidationError("La hora de inicio debe ser anterior a la hora de fin.")

    def __str__(self):
        return f"Reserva {self.id} - {self.placa} ({self.estado})"

# 3) Modelo Vehiculo (Nuevo)
class Vehiculo(models.Model):
    TIPO_CHOICES = [
        ('CARRO', 'CARRO'),
        ('MOTO', 'MOTO'),
    ]
    
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vehiculos')
    placa = models.CharField(max_length=20, unique=True)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    descripcion = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"{self.placa} ({self.tipo})"

# 4) Modelo Incidencia
class Incidencia(models.Model):
    TIPO_CHOICES = [
        ('SIN_RESERVA', 'SIN_RESERVA'),
        ('DANIO_ESPACIO', 'DANIO_ESPACIO'),
        ('OCUPACION_INDEBIDA', 'OCUPACION_INDEBIDA'),
        ('OTRO', 'OTRO'),
    ]

    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES)
    espacio = models.ForeignKey(EspacioParqueadero, on_delete=models.SET_NULL, null=True, blank=True)
    descripcion = models.TextField()
    reportado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    fecha_hora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Incidencia {self.tipo} - {self.fecha_hora}"
