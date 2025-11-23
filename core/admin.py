from django.contrib import admin
from .models import EspacioParqueadero, Reserva, Incidencia

@admin.register(EspacioParqueadero)
class EspacioParqueaderoAdmin(admin.ModelAdmin):
    list_display = ('numero', 'tipo', 'estado')
    list_filter = ('estado', 'tipo')
    search_fields = ('numero',)

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'espacio', 'fecha', 'hora_inicio', 'hora_fin', 'placa', 'estado')
    list_filter = ('estado', 'fecha', 'tipo_vehiculo')
    search_fields = ('placa', 'usuario__username')

@admin.register(Incidencia)
class IncidenciaAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'espacio', 'reportado_por', 'fecha_hora')
    list_filter = ('tipo', 'fecha_hora')
    search_fields = ('descripcion',)
