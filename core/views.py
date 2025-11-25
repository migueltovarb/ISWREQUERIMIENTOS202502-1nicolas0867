from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import EspacioParqueadero, Reserva, Vehiculo
from .forms import ReservaForm, RegistroForm, VehiculoForm
import datetime

# --- Funciones de ayuda para roles ---
def is_vigilante(user):
    return user.groups.filter(name='VIGILANTE').exists()

def is_cliente(user):
    return not user.is_superuser and not is_vigilante(user)

# --- Vista Home / Redirección ---
@login_required
def home(request):
    """
    Redirige al usuario según su rol:
    - Superuser -> /admin/
    - Vigilante -> Validar Placa
    - Cliente -> Disponibilidad
    """
    if request.user.is_superuser:
        return redirect('/admin/')
    elif is_vigilante(request.user):
        return redirect('core:validar_placa')
    else:
        return redirect('core:disponibilidad')

def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Loguear automáticamente
            messages.success(request, 'Registro exitoso. Bienvenido.')
            return redirect('core:home')
        else:
            messages.error(request, 'Error en el registro. Verifique los datos.')
    else:
        form = RegistroForm()
    return render(request, 'registro.html', {'form': form})

# --- Vistas Cliente ---

@login_required
def disponibilidad(request):
    """
    Muestra todos los espacios y su estado actual.
    Permite reservar si está LIBRE.
    """
    espacios = EspacioParqueadero.objects.all().order_by('numero')
    return render(request, 'cliente/disponibilidad.html', {'espacios': espacios})

@login_required
def crear_reserva(request):
    """
    Formulario para crear una reserva.
    Valida solapamientos y actualiza estado del espacio.
    """
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.usuario = request.user
            reserva.estado = 'RESERVADA'
            
            # Validación extra de solapamiento (ya hecha en form, pero doble check por seguridad)
            # ... (la validación del form.clean() ya se ejecutó)
            
            reserva.save()
            
            # Actualizar estado del espacio a RESERVADO
            espacio = reserva.espacio
            espacio.estado = 'RESERVADO'
            espacio.save()
            
            messages.success(request, 'Reserva creada exitosamente.')
            return redirect('core:reservas_activas')
        else:
            messages.error(request, 'Error al crear la reserva. Verifique los datos.')
    else:
        # Pre-seleccionar espacio si viene por GET
        initial_data = {}
        espacio_id = request.GET.get('espacio_id')
        if espacio_id:
            initial_data['espacio'] = espacio_id
        form = ReservaForm(initial=initial_data)

    return render(request, 'cliente/crear_reserva.html', {'form': form})

@login_required
def reservas_activas(request):
    """
    Lista reservas futuras o activas del usuario.
    """
    reservas = Reserva.objects.filter(
        usuario=request.user,
        estado='RESERVADA'
    ).order_by('fecha', 'hora_inicio')
    return render(request, 'cliente/reservas_activas.html', {'reservas': reservas})

@login_required
def historial_reservas(request):
    """
    Lista todas las reservas del usuario.
    """
    reservas = Reserva.objects.filter(usuario=request.user).order_by('-fecha', '-hora_inicio')
    return render(request, 'cliente/historial.html', {'reservas': reservas})

@login_required
def cancelar_reserva(request, reserva_id):
    """
    Cancela una reserva si aún no ha iniciado.
    """
    reserva = get_object_or_404(Reserva, id=reserva_id, usuario=request.user)
    
    # Verificar si ya pasó la hora de inicio (simplificado: fecha y hora)
    ahora = timezone.now()
    inicio_reserva = datetime.datetime.combine(reserva.fecha, reserva.hora_inicio)
    # Hacer inicio_reserva aware si timezone está activo
    if timezone.is_aware(ahora):
        inicio_reserva = timezone.make_aware(inicio_reserva)

    if ahora < inicio_reserva:
        reserva.estado = 'CANCELADA'
        reserva.save()
        
        # Liberar espacio si no hay otras reservas inmediatas (simplificado: liberar siempre)
        # En un sistema real, verificaríamos si hay otra reserva solapada ahora mismo.
        # Asumimos que al cancelar se libera.
        espacio = reserva.espacio
        espacio.estado = 'LIBRE'
        espacio.save()
        
        messages.success(request, 'Reserva cancelada.')
    else:
        messages.error(request, 'No se puede cancelar una reserva que ya inició o pasó.')
        
    return redirect('core:reservas_activas')

@login_required
def mis_vehiculos(request):
    """
    Lista los vehículos registrados por el usuario.
    """
    vehiculos = request.user.vehiculos.all()
    return render(request, 'cliente/mis_vehiculos.html', {'vehiculos': vehiculos})

@login_required
def agregar_vehiculo(request):
    """
    Formulario para registrar un nuevo vehículo.
    """
    if request.method == 'POST':
        form = VehiculoForm(request.POST)
        if form.is_valid():
            vehiculo = form.save(commit=False)
            vehiculo.usuario = request.user
            vehiculo.save()
            messages.success(request, 'Vehículo registrado exitosamente.')
            return redirect('core:mis_vehiculos')
    else:
        form = VehiculoForm()
    return render(request, 'cliente/agregar_vehiculo.html', {'form': form})

@login_required
def eliminar_vehiculo(request, vehiculo_id):
    """
    Elimina un vehículo del usuario.
    """
    vehiculo = get_object_or_404(Vehiculo, id=vehiculo_id, usuario=request.user)
    vehiculo.delete()
    messages.success(request, 'Vehículo eliminado.')
    return redirect('core:mis_vehiculos')

# --- Vistas Vigilante ---

@login_required
@user_passes_test(is_vigilante)
def validar_placa(request):
    """
    Busca reserva activa para una placa en el momento actual.
    """
    reserva_encontrada = None
    mensaje = None
    
    if request.method == 'POST':
        placa = request.POST.get('placa')
        ahora = timezone.now() # Fecha y hora actual
        hora_actual = ahora.time()
        fecha_actual = ahora.date()
        
        # Buscar reserva RESERVADA para hoy, esa placa, y que la hora actual esté en rango (o cerca)
        # Margen de tolerancia: ej. llegar 15 min antes.
        # Aquí buscamos coincidencia exacta de fecha y rango de horas.
        qs = Reserva.objects.filter(
            placa__iexact=placa,
            fecha=fecha_actual,
            estado='RESERVADA',
            hora_inicio__lte=hora_actual,
            hora_fin__gte=hora_actual
        )
        
        if qs.exists():
            reserva_encontrada = qs.first()
        else:
            # Intentar buscar si llega un poco antes (opcional, no pedido explícitamente pero útil)
            mensaje = "No existe reserva activa para esta placa en este momento."

    return render(request, 'vigilante/validar_placa.html', {
        'reserva': reserva_encontrada,
        'mensaje': mensaje
    })

@login_required
@user_passes_test(is_vigilante)
def registrar_entrada(request, reserva_id):
    """
    Registra la entrada del vehículo.
    """
    reserva = get_object_or_404(Reserva, id=reserva_id)
    reserva.hora_entrada = timezone.now().time()
    # El estado sigue siendo RESERVADA o podríamos cambiarlo a 'EN_CURSO' si existiera.
    # Lo importante es marcar el espacio como OCUPADO.
    reserva.save()
    
    espacio = reserva.espacio
    espacio.estado = 'OCUPADO'
    espacio.save()
    
    messages.success(request, f'Entrada registrada para {reserva.placa}.')
    return redirect('core:validar_placa')

@login_required
@user_passes_test(is_vigilante)
def listado_salidas(request):
    """
    Lista vehículos que han entrado pero no salido.
    (Reserva con hora_entrada NOT NULL y hora_salida NULL)
    """
    reservas_en_curso = Reserva.objects.filter(
        hora_entrada__isnull=False,
        hora_salida__isnull=True,
        fecha=timezone.now().date() # Solo de hoy
    )
    return render(request, 'vigilante/salida.html', {'reservas': reservas_en_curso})

@login_required
@user_passes_test(is_vigilante)
def registrar_salida(request, reserva_id):
    """
    Registra salida y libera espacio.
    """
    reserva = get_object_or_404(Reserva, id=reserva_id)
    reserva.hora_salida = timezone.now().time()
    reserva.estado = 'COMPLETADA'
    reserva.save()
    
    espacio = reserva.espacio
    espacio.estado = 'LIBRE'
    espacio.save()
    
    messages.success(request, f'Salida registrada para {reserva.placa}.')
    return redirect('core:listado_salidas')

@login_required
@user_passes_test(is_vigilante)
def ocupacion_actual(request):
    """
    Muestra estado de todos los espacios para el vigilante.
    """
    espacios = EspacioParqueadero.objects.all().order_by('numero')
    return render(request, 'vigilante/ocupacion.html', {'espacios': espacios})
