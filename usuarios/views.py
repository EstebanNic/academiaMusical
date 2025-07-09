from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Usuario

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
    profesores = Usuario.objects.filter(rol=Usuario.Rol.PROFESOR)
    return render(request, 'usuarios/admin_profesores.html', {'profesores': profesores})
