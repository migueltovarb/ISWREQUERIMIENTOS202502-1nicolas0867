from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'core'

urlpatterns = [
    # Home y Auth
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name="login.html"), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='core:login'), name='logout'),
    path('registro/', views.registro, name='registro'),

    # Password Reset
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset_form.html', email_template_name='password_reset_email.html', success_url='/password_reset/done/'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html', success_url='/reset/done/'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),


    # Cliente
    path('cliente/disponibilidad/', views.disponibilidad, name='disponibilidad'),
    path('cliente/reservar/', views.crear_reserva, name='crear_reserva'),
    path('cliente/reservas/', views.reservas_activas, name='reservas_activas'),
    path('cliente/historial/', views.historial_reservas, name='historial'),
    path('cliente/cancelar/<int:reserva_id>/', views.cancelar_reserva, name='cancelar_reserva'),
    
    # Vehículos
    path('cliente/vehiculos/', views.mis_vehiculos, name='mis_vehiculos'),
    path('cliente/vehiculos/agregar/', views.agregar_vehiculo, name='agregar_vehiculo'),
    path('cliente/vehiculos/eliminar/<int:vehiculo_id>/', views.eliminar_vehiculo, name='eliminar_vehiculo'),

    # Vigilante
    path('vigilante/validar/', views.validar_placa, name='validar_placa'),
    path('vigilante/entrada/<int:reserva_id>/', views.registrar_entrada, name='registrar_entrada'),
    path('vigilante/salida/', views.listado_salidas, name='listado_salidas'),
    path('vigilante/salida/<int:reserva_id>/', views.registrar_salida, name='registrar_salida'),
    path('vigilante/ocupacion/', views.ocupacion_actual, name='ocupacion_actual'),
]
