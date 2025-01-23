from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from .models import Usuarios
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.cache import cache
from django.contrib import messages

def index(request):
    return render(request, 'Blyss/index.html', {'mensaje': '¡Bienvenido a Blyss!'})

def registro_view(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellidos = request.POST.get('apellidos')
        correo = request.POST.get('correo')
        password = request.POST.get('password')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')

        # Verificar que todos los campos estén completos
        if not all([nombre, apellidos, correo, password, fecha_nacimiento]):
            return JsonResponse({'status': 'error', 'message': 'Todos los campos son requeridos.'})

        # Validar formato del correo
        try:
            validate_email(correo)
        except ValidationError:
            return JsonResponse({'status': 'error', 'message': 'El correo electrónico no es válido.'})

        # Validar longitud de la contraseña
        if len(password) < 6:
            return JsonResponse({'status': 'error', 'message': 'La contraseña debe tener al menos 6 caracteres.'})

        # Validar si el correo ya está registrado
        if Usuarios.objects.filter(correo=correo).exists():
            return JsonResponse({'status': 'error', 'message': 'El correo ya está registrado.'})

        # Validar formato de la fecha de nacimiento
        try:
            fecha_nacimiento = datetime.strptime(fecha_nacimiento, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'Fecha de nacimiento no válida.'})

        # Validar que la fecha de nacimiento sea razonable (mayor de 18 años)
        hoy = datetime.today().date()
        if (hoy.year - fecha_nacimiento.year) < 18:
            return JsonResponse({'status': 'error', 'message': 'Debes tener al menos 18 años.'})

        # Crear el usuario
        usuario = Usuarios.objects.create(
            Nombre=nombre,
            Apellidos=apellidos,
            correo=correo,
            password=make_password(password),
            FechaDeNacimiento=fecha_nacimiento
        )
        return JsonResponse({'status': 'success', 'message': 'Usuario registrado exitosamente.'})

    return render(request, 'Blyss/register.html')

# Configuración
MAX_ATTEMPTS = 5  # Número máximo de intentos permitidos
BLOCK_DURATION = 600  # Duración del bloqueo en segundos (10 minutos)

def get_client_ip(request):
    """Obtiene la IP del cliente desde el encabezado de la solicitud."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def login_view(request):
    ip = get_client_ip(request)  # Obtener la IP del cliente
    key = f"login_attempts_{ip}"  # Clave para rastrear intentos fallidos
    attempts = cache.get(key, 0)  # Recuperar intentos fallidos de la caché

    if attempts >= MAX_ATTEMPTS:
        # Bloquear acceso por exceder intentos fallidos
        return JsonResponse({
            'status': 'error',
            'message': 'Demasiados intentos fallidos. Inténtalo de nuevo en 10 minutos.'
        })

    if request.method == 'POST':
        correo = request.POST.get('correo')
        password = request.POST.get('password')

        if not correo or not password:
            return JsonResponse({'status': 'error', 'message': 'Todos los campos son requeridos.'})

        usuario = authenticate(request, username=correo, password=password)
        if usuario is not None:
            # Inicio de sesión exitoso
            login(request, usuario)
            cache.delete(key)  # Reiniciar intentos fallidos al iniciar sesión
            return JsonResponse({'status': 'success', 'message': 'Inicio de sesión exitoso.'})
        else:
            # Incrementar contador de intentos fallidos
            attempts += 1
            cache.set(key, attempts, BLOCK_DURATION)
            return JsonResponse({
                'status': 'error',
                'message': f'Credenciales inválidas. Intentos restantes: {MAX_ATTEMPTS - attempts}'
            })

    return render(request, 'Blyss/login.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')