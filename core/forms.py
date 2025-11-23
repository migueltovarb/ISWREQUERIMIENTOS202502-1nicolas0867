from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Q
from .models import Reserva, EspacioParqueadero, Vehiculo

class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['espacio', 'fecha', 'hora_inicio', 'hora_fin', 'tipo_vehiculo', 'placa']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'hora_fin': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'espacio': forms.Select(attrs={'class': 'form-select'}),
            'tipo_vehiculo': forms.Select(attrs={'class': 'form-select'}),
            'placa': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        espacio = cleaned_data.get('espacio')
        fecha = cleaned_data.get('fecha')
        hora_inicio = cleaned_data.get('hora_inicio')
        hora_fin = cleaned_data.get('hora_fin')

        if hora_inicio and hora_fin:
            if hora_inicio >= hora_fin:
                raise ValidationError("La hora de inicio debe ser anterior a la hora de fin.")

            # Validar solapamiento de reservas
            # Se busca si existe alguna reserva para el mismo espacio y fecha
            # que se solape en el rango de horas.
            # Solapamiento: (InicioA < FinB) y (FinA > InicioB)
            solapamientos = Reserva.objects.filter(
                espacio=espacio,
                fecha=fecha,
                estado='RESERVADA' # Solo validar contra reservas activas
            ).filter(
                Q(hora_inicio__lt=hora_fin) & Q(hora_fin__gt=hora_inicio)
            )

            if solapamientos.exists():
                raise ValidationError("El espacio ya está reservado en ese horario.")

        return cleaned_data

class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = ['placa', 'tipo', 'descripcion']
        widgets = {
            'placa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: ABC-123'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Toyota Corolla Rojo'}),
        }

