from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Usuario
from django.db import IntegrityError
from django.contrib.auth import logout


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

def logout_view(request):
    list(messages.get_messages(request))  # Esto borra los mensajes pendientes
    logout(request)
    return redirect('login')

@login_required
def admin_dashboard(request):
    if request.user.rol != Usuario.Rol.ADMIN:
        return redirect('login')  # o a otra página de acceso denegado
    return render(request, 'usuarios/admin_dashboard.html', {
        'active_tab': 'inicio'
    })

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
        profesor_id = request.POST.get('profesor_id')
        # Eliminar profesor si el form de eliminación fue enviado
        if request.POST.get('eliminar_profesor') == '1' and profesor_id:
            try:
                profesor = Usuario.objects.get(id=profesor_id, rol=Usuario.Rol.PROFESOR)
                profesor.delete()
                messages.success(request, 'Profesor eliminado exitosamente.')
            except Usuario.DoesNotExist:
                messages.error(request, 'Profesor no encontrado.')
            return redirect('admin_profesores')
        elif profesor_id:
            # Edición de profesor
            try:
                profesor = Usuario.objects.get(id=profesor_id, rol=Usuario.Rol.PROFESOR)
                profesor.cedula = request.POST.get('cedula', '')
                profesor.first_name = request.POST.get('first_name', '')
                profesor.last_name = request.POST.get('last_name', '')
                profesor.email = request.POST.get('email', '')
                profesor.username = request.POST.get('email', '')
                profesor.instrumento = request.POST.get('instrumento', '')
                profesor.telefono = request.POST.get('telefono', '')
                profesor.direccion = request.POST.get('direccion', '')
                profesor.save()
                messages.success(request, 'Profesor actualizado exitosamente.')
            except Usuario.DoesNotExist:
                messages.error(request, 'Profesor no encontrado.')
            return redirect('admin_profesores')
        else:
            # Alta de profesor
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
    return render(request, 'usuarios/admin_profesores.html', {'profesores': profesores ,
    'active_tab': 'profesores'})

@login_required
def admin_cursos(request):
    return render(request, 'usuarios/admin_cursos.html', {
        'active_tab': 'cursos'
    })

@login_required
def admin_estudiantes(request):
    if request.user.rol != Usuario.Rol.ADMIN:
        return redirect('login')
    if request.method == 'POST':
        estudiante_id = request.POST.get('estudiante_id')
        # Eliminar estudiante si el form de eliminación fue enviado
        if request.POST.get('eliminar_estudiante') == '1' and estudiante_id:
            try:
                estudiante = Usuario.objects.get(id=estudiante_id, rol=Usuario.Rol.ESTUDIANTE)
                estudiante.delete()
                messages.success(request, 'Estudiante eliminado exitosamente.')
            except Usuario.DoesNotExist:
                messages.error(request, 'Estudiante no encontrado.')
            return redirect('admin_estudiantes')
        elif estudiante_id:
            # Edición de estudiante
            try:
                estudiante = Usuario.objects.get(id=estudiante_id, rol=Usuario.Rol.ESTUDIANTE)
                estudiante.cedula = request.POST.get('cedula', '')
                estudiante.first_name = request.POST.get('first_name', '')
                estudiante.last_name = request.POST.get('last_name', '')
                estudiante.email = request.POST.get('email', '')
                estudiante.username = request.POST.get('email', '')
                estudiante.instrumento = request.POST.get('instrumento', '')
                estudiante.telefono = request.POST.get('telefono', '')
                estudiante.direccion = request.POST.get('direccion', '')
                estudiante.save()
                messages.success(request, 'Estudiante actualizado exitosamente.')
            except Usuario.DoesNotExist:
                messages.error(request, 'Estudiante no encontrado.')
            return redirect('admin_estudiantes')
        else:
            # Alta de estudiante
            cedula = request.POST.get('cedula', '')
            first_name = request.POST.get('first_name', '')
            last_name = request.POST.get('last_name', '')
            email = request.POST.get('email', '')
            instrumento = request.POST.get('instrumento', '')
            telefono = request.POST.get('telefono', '')
            direccion = request.POST.get('direccion', '')
            password = request.POST.get('password', '')
            confirm_password = request.POST.get('confirm_password', '')
            rol = Usuario.Rol.ESTUDIANTE

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
                    messages.success(request, 'Estudiante registrado exitosamente.')
                    return redirect('admin_estudiantes')
                except IntegrityError:
                    messages.error(request, 'Error al registrar el estudiante. Intente con otro email.')
    estudiantes = Usuario.objects.filter(rol=Usuario.Rol.ESTUDIANTE)
    return render(request, 'usuarios/admin_estudiantes.html', {'estudiantes': estudiantes, 'active_tab': 'estudiantes'})
