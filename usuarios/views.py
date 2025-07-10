from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Usuario
from django.db import IntegrityError

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Redirigir según el rol
            if user.rol == Usuario.Rol.ADMIN:
                return redirect('admin_dashboard')
            elif user.rol == Usuario.Rol.PROFESOR:
                return redirect('profesor_dashboard')
            elif user.rol == Usuario.Rol.ESTUDIANTE:
                return redirect('estudiante_dashboard')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')

    return render(request, 'usuarios/login.html')

@login_required
def admin_dashboard(request):
    if request.user.rol != Usuario.Rol.ADMIN:
        return redirect('login')  # o a otra página de acceso denegado
    return render(request, 'usuarios/admin_dashboard.html')

@login_required
def profesor_dashboard(request):
    return render(request, 'usuarios/profesor_dashboard.html')

@login_required
def estudiante_dashboard(request):
    return render(request, 'usuarios/estudiante_dashboard.html')

@login_required
def admin_profesores(request):
    if request.user.rol != Usuario.Rol.ADMIN:
        return redirect('login')
    if request.method == 'POST':
        cedula = request.POST.get('cedula', '')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        email = request.POST.get('email', '')
        instrumento = request.POST.get('instrumento', '')
        telefono = request.POST.get('telefono', '')
        direccion = request.POST.get('direccion', '')
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        rol = Usuario.Rol.PROFESOR

        if password != confirm_password:
            messages.error(request, 'Las contraseñas no coinciden.')
        elif Usuario.objects.filter(email=email).exists():
            messages.error(request, 'El email ya está registrado.')
        else:
            try:
                usuario = Usuario.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    rol=rol,
                    cedula=cedula,
                    telefono=telefono,
                    direccion=direccion,
                    instrumento=instrumento,
                    is_active=True
                )
                messages.success(request, 'Profesor registrado exitosamente.')
                return redirect('admin_profesores')
            except IntegrityError:
                messages.error(request, 'Error al registrar el profesor. Intente con otro email.')
    profesores = Usuario.objects.filter(rol=Usuario.Rol.PROFESOR)
    return render(request, 'usuarios/admin_profesores.html', {'profesores': profesores})
