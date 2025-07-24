from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Usuario
from django.db import IntegrityError
from django.contrib.auth import logout
from cursos.models import Curso, Nivel
from horarios.models import Horario
from matriculas.models import Matricula
from pagos.models import Pago, EstadoPago
from asistencias.models import Asistencia, EstadoAsistencia
from datetime import datetime, date
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import models
import json

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
        return redirect('login')
    
    # Obtener métricas del dashboard
    total_estudiantes = Usuario.objects.filter(rol=Usuario.Rol.ESTUDIANTE).count()
    total_profesores = Usuario.objects.filter(rol=Usuario.Rol.PROFESOR).count()
    total_cursos = Curso.objects.count()
    total_matriculas = Matricula.objects.filter(estado='ACTIVA').count()
    
    # Obtener pagos pendientes (primeros 5)
    pagos_pendientes = Pago.objects.filter(estado=EstadoPago.PENDIENTE).select_related(
        'matricula__estudiante', 'matricula__clase__curso'
    )[:5]
    
    # Obtener clases de hoy
    fecha_hoy = date.today()
    clases_hoy = Horario.objects.filter(
        fecha_inicio__lte=fecha_hoy,
        fecha_fin__gte=fecha_hoy
    ).select_related('curso', 'profesor').order_by('hora_inicio')
    
    return render(request, 'usuarios/admin_dashboard.html', {
        'active_tab': 'inicio',
        'total_estudiantes': total_estudiantes,
        'total_profesores': total_profesores,
        'total_cursos': total_cursos,
        'total_matriculas': total_matriculas,
        'pagos_pendientes': pagos_pendientes,
        'clases_hoy': clases_hoy,
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
    
    # Variables para controlar modales
    mostrar_modal_duplicado = False
    mostrar_modal_duplicado_edicion = False
    
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
                cedula = request.POST.get('cedula', '')
                email = request.POST.get('email', '')
                telefono = request.POST.get('telefono', '')
                
                # Validar duplicados en edición (excluyendo el profesor actual)
                duplicados_edicion = []
                
                if cedula and Usuario.objects.filter(cedula=cedula).exclude(id=profesor.id).exists():
                    duplicados_edicion.append(f'Ya existe un usuario con la cédula: {cedula}')
                
                if email and Usuario.objects.filter(email=email).exclude(id=profesor.id).exists():
                    duplicados_edicion.append(f'Ya existe un usuario con el email: {email}')
                
                if telefono and Usuario.objects.filter(telefono=telefono).exclude(id=profesor.id).exists():
                    duplicados_edicion.append(f'Ya existe un usuario con el teléfono: {telefono}')
                
                if duplicados_edicion:
                    # Mostrar modal de duplicado para edición
                    mostrar_modal_duplicado_edicion = True
                else:
                    # Solo actualizar si no hay duplicados
                    profesor.cedula = cedula
                    profesor.first_name = request.POST.get('first_name', '')
                    profesor.last_name = request.POST.get('last_name', '')
                    profesor.email = email
                    profesor.username = email
                    profesor.instrumento = request.POST.get('instrumento', '')
                    profesor.telefono = telefono
                    profesor.direccion = request.POST.get('direccion', '')
                    profesor.save()
                    messages.success(request, 'Profesor actualizado exitosamente.')
                    return redirect('admin_profesores')
                    
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

            # Validaciones
            if password != confirm_password:
                messages.error(request, 'Las contraseñas no coinciden.')
                return redirect('admin_profesores')
            
            # Validar duplicados de manera simple
            duplicado_encontrado = False
            
            if cedula and Usuario.objects.filter(cedula=cedula).exists():
                duplicado_encontrado = True
            
            if email and Usuario.objects.filter(email=email).exists():
                duplicado_encontrado = True
            
            if telefono and Usuario.objects.filter(telefono=telefono).exists():
                duplicado_encontrado = True
            
            if duplicado_encontrado:
                mostrar_modal_duplicado = True
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
                    mostrar_modal_duplicado = True
    
    profesores = Usuario.objects.filter(rol=Usuario.Rol.PROFESOR)
    return render(request, 'usuarios/admin_profesores.html', {
        'profesores': profesores,
        'active_tab': 'profesores',
        'mostrar_modal_duplicado': mostrar_modal_duplicado,
        'mostrar_modal_duplicado_edicion': mostrar_modal_duplicado_edicion
    })

@login_required
def admin_cursos(request):
    if request.user.rol != Usuario.Rol.ADMIN:
        return redirect('login')

    # Obtener profesores desde Usuario (rol=PROFESOR)
    profesores = Usuario.objects.filter(rol=Usuario.Rol.PROFESOR)
    curso_niveles = Nivel.choices
    
    # Lista predefinida de cursos musicales
    cursos_musicales = [
        'Curso de Piano',
        'Curso de Guitarra',
        'Curso de Violín',
        'Curso de Canto',
        'Curso de Batería',
        'Curso de Saxofón',
        'Curso de Flauta',
        'Curso de Cello',
        'Curso de Trompeta',
        'Curso de Clarinete',
        'Curso de Contrabajo',
        'Curso de Armónica',
        'Curso de Ukelele',
        'Curso de Teclado',
        'Teoría Musical',
        'Composición Musical',
        'Producción Musical',
    ]
    
    # Variables para controlar modales
    mostrar_modal_duplicado_curso = False
    mostrar_modal_profesor_ocupado = False

    if request.method == 'POST':
        # Eliminar curso
        if request.POST.get('eliminar_curso') == '1':
            curso_id = request.POST.get('curso_id')
            try:
                curso = Curso.objects.get(id=curso_id)
                curso.delete()
                messages.success(request, 'Curso eliminado exitosamente.')
            except Curso.DoesNotExist:
                messages.error(request, 'Curso no encontrado.')
            return redirect('admin_cursos')

        # Editar curso
        elif request.POST.get('curso_id'):
            curso_id = request.POST.get('curso_id')
            try:
                curso = Curso.objects.get(id=curso_id)
                nombre = request.POST.get('nombre', '')
                nivel = request.POST.get('nivel', '')
                precio = request.POST.get('precio', 0.00)
                profesor_id = request.POST.get('profesor')
                # No procesar descripción
                
                # Validar duplicado de curso (excluyendo el curso actual)
                if Curso.objects.filter(nombre=nombre, nivel=nivel).exclude(id=curso.id).exists():
                    mostrar_modal_duplicado_curso = True
                else:
                    # Validar profesor no ocupado en otro curso del mismo tipo (excluyendo el curso actual)
                    if profesor_id and profesor_id != '':
                        try:
                            profesor_usuario = Usuario.objects.get(id=profesor_id, rol=Usuario.Rol.PROFESOR)
                            # Verificar si el profesor ya está en otro curso del mismo nombre (excluyendo el actual)
                            if Curso.objects.filter(profesor=profesor_usuario, nombre=nombre).exclude(id=curso.id).exists():
                                mostrar_modal_profesor_ocupado = True
                            else:
                                # Actualizar curso (sin descripción)
                                curso.nombre = nombre
                                curso.nivel = nivel
                                curso.precio = precio
                                curso.profesor = profesor_usuario
                                curso.save()
                                messages.success(request, 'Curso actualizado exitosamente.')
                                return redirect('admin_cursos')
                        except Usuario.DoesNotExist:
                            curso.profesor = None
                            curso.nombre = nombre
                            curso.nivel = nivel
                            curso.precio = precio
                            curso.save()
                            messages.success(request, 'Curso actualizado exitosamente.')
                            return redirect('admin_cursos')
                    else:
                        # Sin profesor asignado (sin descripción)
                        curso.nombre = nombre
                        curso.nivel = nivel
                        curso.precio = precio
                        curso.profesor = None
                        curso.save()
                        messages.success(request, 'Curso actualizado exitosamente.')
                        return redirect('admin_cursos')
                        
            except Curso.DoesNotExist:
                messages.error(request, 'Curso no encontrado.')
                return redirect('admin_cursos')

        # Agregar curso
        else:
            nombre = request.POST.get('nombre', '')
            nivel = request.POST.get('nivel', '')
            precio = request.POST.get('precio', 0.00)
            profesor_id = request.POST.get('profesor')
            # No procesar descripción
            
            # Validar duplicado de curso
            if Curso.objects.filter(nombre=nombre, nivel=nivel).exists():
                mostrar_modal_duplicado_curso = True
            else:
                profesor = None
                if profesor_id and profesor_id != '':
                    try:
                        profesor = Usuario.objects.get(id=profesor_id, rol=Usuario.Rol.PROFESOR)
                        # Verificar si el profesor ya está en otro curso del mismo nombre
                        if Curso.objects.filter(profesor=profesor, nombre=nombre).exists():
                            mostrar_modal_profesor_ocupado = True
                        else:
                            # Crear curso (sin descripción)
                            Curso.objects.create(
                                nombre=nombre,
                                nivel=nivel,
                                precio=precio,
                                profesor=profesor
                            )
                            messages.success(request, 'Curso registrado exitosamente.')
                            return redirect('admin_cursos')
                    except Usuario.DoesNotExist:
                        # Crear curso sin profesor (sin descripción)
                        Curso.objects.create(
                            nombre=nombre,
                            nivel=nivel,
                            precio=precio,
                            profesor=None
                        )
                        messages.success(request, 'Curso registrado exitosamente.')
                        return redirect('admin_cursos')
                else:
                    # Crear curso sin profesor (sin descripción)
                    Curso.objects.create(
                        nombre=nombre,
                        nivel=nivel,
                        precio=precio,
                        profesor=None
                    )
                    messages.success(request, 'Curso registrado exitosamente.')
                    return redirect('admin_cursos')

    cursos = Curso.objects.select_related('profesor').all().order_by('nombre', 'nivel')
    return render(request, 'usuarios/admin_cursos.html', {
        'active_tab': 'cursos',
        'cursos': cursos,
        'profesores': profesores,
        'curso_niveles': curso_niveles,
        'cursos_musicales': cursos_musicales,
        'mostrar_modal_duplicado_curso': mostrar_modal_duplicado_curso,
        'mostrar_modal_profesor_ocupado': mostrar_modal_profesor_ocupado,
    })

@login_required
def admin_estudiantes(request):
    if request.user.rol != Usuario.Rol.ADMIN:
        return redirect('login')
    
    # Variables para controlar modales
    mostrar_modal_duplicado = False
    mostrar_modal_duplicado_edicion = False
    
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
                cedula = request.POST.get('cedula', '')
                email = request.POST.get('email', '')
                telefono = request.POST.get('telefono', '')
                
                # Validar duplicados en edición (excluyendo el estudiante actual)
                duplicados_edicion = []
                
                if cedula and Usuario.objects.filter(cedula=cedula).exclude(id=estudiante.id).exists():
                    duplicados_edicion.append(f'Ya existe un usuario con la cédula: {cedula}')
                
                if email and Usuario.objects.filter(email=email).exclude(id=estudiante.id).exists():
                    duplicados_edicion.append(f'Ya existe un usuario con el email: {email}')
                
                if telefono and Usuario.objects.filter(telefono=telefono).exclude(id=estudiante.id).exists():
                    duplicados_edicion.append(f'Ya existe un usuario con el teléfono: {telefono}')
                
                if duplicados_edicion:
                    # Mostrar modal de duplicado para edición
                    mostrar_modal_duplicado_edicion = True
                else:
                    # Solo actualizar si no hay duplicados
                    estudiante.cedula = cedula
                    estudiante.first_name = request.POST.get('first_name', '')
                    estudiante.last_name = request.POST.get('last_name', '')
                    estudiante.email = email
                    estudiante.username = email
                    # No actualizar instrumento para estudiantes
                    estudiante.telefono = telefono
                    estudiante.direccion = request.POST.get('direccion', '')
                    estudiante.save()
                    messages.success(request, 'Estudiante actualizado exitosamente.')
                    return redirect('admin_estudiantes')
                    
            except Usuario.DoesNotExist:
                messages.error(request, 'Estudiante no encontrado.')
                return redirect('admin_estudiantes')
        else:
            # Alta de estudiante
            cedula = request.POST.get('cedula', '')
            first_name = request.POST.get('first_name', '')
            last_name = request.POST.get('last_name', '')
            email = request.POST.get('email', '')
            # No obtener instrumento para estudiantes
            telefono = request.POST.get('telefono', '')
            direccion = request.POST.get('direccion', '')
            password = request.POST.get('password', '')
            confirm_password = request.POST.get('confirm_password', '')
            rol = Usuario.Rol.ESTUDIANTE

            # Validaciones
            if password != confirm_password:
                messages.error(request, 'Las contraseñas no coinciden.')
                return redirect('admin_estudiantes')
            
            # Validar duplicados de manera simple
            duplicado_encontrado = False
            
            if cedula and Usuario.objects.filter(cedula=cedula).exists():
                duplicado_encontrado = True
            
            if email and Usuario.objects.filter(email=email).exists():
                duplicado_encontrado = True
            
            if telefono and Usuario.objects.filter(telefono=telefono).exists():
                duplicado_encontrado = True
            
            if duplicado_encontrado:
                mostrar_modal_duplicado = True
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
                        # No asignar instrumento para estudiantes
                        is_active=True
                    )
                    messages.success(request, 'Estudiante registrado exitosamente.')
                    return redirect('admin_estudiantes')
                except IntegrityError:
                    mostrar_modal_duplicado = True
    
    estudiantes = Usuario.objects.filter(rol=Usuario.Rol.ESTUDIANTE)
    return render(request, 'usuarios/admin_estudiantes.html', {
        'estudiantes': estudiantes,
        'active_tab': 'estudiantes',
        'mostrar_modal_duplicado': mostrar_modal_duplicado,
        'mostrar_modal_duplicado_edicion': mostrar_modal_duplicado_edicion
    })

@login_required
def admin_clases(request):
    if request.user.rol != Usuario.Rol.ADMIN:
        return redirect('login')

    cursos = Curso.objects.all()
    profesores = Usuario.objects.filter(rol=Usuario.Rol.PROFESOR)
    clases = Horario.objects.select_related('curso', 'profesor').all().order_by('-fecha_inicio', '-hora_inicio')

    if request.method == 'POST':
        clase_id = request.POST.get('clase_id')
        # Eliminar clase
        if request.POST.get('eliminar_clase') == '1' and clase_id:
            try:
                clase = Horario.objects.get(id=clase_id)
                clase.delete()
                messages.success(request, 'Clase eliminada exitosamente.')
            except Horario.DoesNotExist:
                messages.error(request, 'Clase no encontrada.')
            return redirect('admin_clases')
        # Editar clase
        elif clase_id:
            try:
                clase = Horario.objects.get(id=clase_id)
                clase.curso_id = request.POST.get('curso', '')
                clase.profesor_id = request.POST.get('profesor', '')
                clase.fecha_inicio = request.POST.get('fecha_inicio', '')
                clase.fecha_fin = request.POST.get('fecha_fin', '')
                clase.hora_inicio = request.POST.get('hora_inicio', '')
                clase.hora_fin = request.POST.get('hora_fin', '')
                clase.descripcion = request.POST.get('descripcion', '')
                clase.save()
                messages.success(request, 'Clase actualizada exitosamente.')
            except Horario.DoesNotExist:
                messages.error(request, 'Clase no encontrada.')
            return redirect('admin_clases')
        # Agregar clase
        else:
            curso_id = request.POST.get('curso', '')
            profesor_id = request.POST.get('profesor', '')
            fecha_inicio = request.POST.get('fecha_inicio', '')
            fecha_fin = request.POST.get('fecha_fin', '')
            hora_inicio = request.POST.get('hora_inicio', '')
            hora_fin = request.POST.get('hora_fin', '')
            descripcion = request.POST.get('descripcion', '')
            try:
                Horario.objects.create(
                    curso_id=curso_id,
                    profesor_id=profesor_id,
                    fecha_inicio=fecha_inicio,
                    fecha_fin=fecha_fin,
                    hora_inicio=hora_inicio,
                    hora_fin=hora_fin,
                    descripcion=descripcion
                )
                messages.success(request, 'Clase registrada exitosamente.')
            except Exception:
                messages.error(request, 'Error al registrar la clase.')
            return redirect('admin_clases')

    return render(request, 'usuarios/admin_clases.html', {
        'active_tab': 'horarios',
        'clases': clases,
        'cursos': cursos,
        'profesores': profesores
    })

@login_required
def admin_matriculas(request):
    if request.method == 'POST':
        estudiante_id = request.POST.get('estudiante')
        clase_id = request.POST.get('clase')
        observaciones = request.POST.get('observaciones')

        # Eliminar matrícula
        if request.POST.get('eliminar_matricula') == '1' and request.POST.get('matricula_id'):
            matricula_id = request.POST.get('matricula_id')
            try:
                matricula = Matricula.objects.get(id=matricula_id)
                matricula.delete()
                messages.success(request, "Matrícula eliminada exitosamente.")
            except Matricula.DoesNotExist:
                messages.error(request, "Matrícula no encontrada.")
            return redirect('admin_matriculas')

        try:
            estudiante = Usuario.objects.get(id=estudiante_id, rol=Usuario.Rol.ESTUDIANTE)
            clase = Horario.objects.get(id=clase_id)

            if Matricula.objects.filter(estudiante=estudiante, clase=clase).exists():
                messages.error(request, "Este estudiante ya está matriculado en esta clase.")
            else:
                matricula = Matricula.objects.create(
                    estudiante=estudiante,
                    clase=clase,
                    observaciones=observaciones
                )
                
                # Crear automáticamente el pago pendiente
                if clase.curso and clase.curso.precio > 0:
                    Pago.objects.create(
                        matricula=matricula,
                        monto=clase.curso.precio,
                        estado=EstadoPago.PENDIENTE,
                        observaciones=f"Pago automático generado para el curso {clase.curso.nombre}"
                    )
                
                messages.success(request, "Matrícula registrada exitosamente y pago pendiente creado.")
                return redirect('admin_matriculas')

        except (Usuario.DoesNotExist, Horario.DoesNotExist):
            messages.error(request, "Estudiante o clase inválido.")

    # GET o POST con errores: mostrar datos
    matriculas = Matricula.objects.select_related('estudiante', 'clase', 'clase__curso', 'clase__profesor')
    estudiantes = Usuario.objects.filter(rol=Usuario.Rol.ESTUDIANTE)
    clases = Horario.objects.select_related('curso', 'profesor').all().order_by('-fecha_inicio', '-hora_inicio')

    return render(request, 'usuarios/admin_matriculas.html', {
        'matriculas': matriculas,
        'estudiantes': estudiantes,
        'clases': clases,
        'active_tab': 'matriculas',
    })

@login_required
def admin_pagos(request):
    if request.user.rol != Usuario.Rol.ADMIN:
        return redirect('login')

    pagos = Pago.objects.select_related('matricula', 'matricula__estudiante', 'matricula__clase', 'matricula__clase__curso').order_by('-fecha_pago')
    matriculas = Matricula.objects.select_related('estudiante', 'clase', 'clase__curso').all()

    if request.method == 'POST':
        matricula_id = request.POST.get('matricula')
        monto_pago = float(request.POST.get('monto', 0))
        estado = request.POST.get('estado', EstadoPago.PENDIENTE)
        observaciones = request.POST.get('observaciones', '')

        try:
            matricula = Matricula.objects.get(id=matricula_id)
            
            # Buscar el pago pendiente existente para esta matrícula
            pago_existente = Pago.objects.filter(
                matricula=matricula, 
                estado=EstadoPago.PENDIENTE
            ).first();
            
            if pago_existente:
                # Actualizar el pago existente
                nuevo_monto = float(pago_existente.monto) - monto_pago
                
                if nuevo_monto <= 0:
                    # Si el monto es 0 o menor, marcar como pagado
                    pago_existente.monto = 0
                    pago_existente.estado = EstadoPago.PAGADO
                    pago_existente.observaciones = f"{pago_existente.observaciones or ''} | Pago completado con ${monto_pago}"
                else:
                    # Reducir el monto pendiente
                    pago_existente.monto = nuevo_monto
                    pago_existente.observaciones = f"{pago_existente.observaciones or ''} | Pago parcial de ${monto_pago}"
                
                pago_existente.save()
                
                # Crear un registro del pago realizado si es necesario (opcional)
                if estado == EstadoPago.PAGADO:
                    Pago.objects.create(
                        matricula=matricula,
                        monto=monto_pago,
                        estado=EstadoPago.PAGADO,
                        observaciones=f"Pago realizado: ${monto_pago}. {observaciones}"
                    )
                
                messages.success(request, f'Pago de ${monto_pago} procesado exitosamente. Saldo restante: ${nuevo_monto if nuevo_monto > 0 else 0}')
            else:
                # Si no hay pago pendiente, crear uno nuevo
                Pago.objects.create(
                    matricula=matricula,
                    monto=monto_pago,
                    estado=estado,
                    observaciones=observaciones
                )
                messages.success(request, 'Pago registrado exitosamente.')
                
            return redirect('admin_pagos')
            
        except Matricula.DoesNotExist:
            messages.error(request, 'Matrícula no encontrada.')

    return render(request, 'usuarios/admin_pagos.html', {
        'active_tab': 'pagos',
        'pagos': pagos,
        'matriculas': matriculas,
        'estados_pago': EstadoPago.choices,
    })

@login_required
def admin_asistencias(request):
    if request.user.rol != Usuario.Rol.ADMIN:
        return redirect('login')

    # Obtener todas las asistencias
    asistencias = Asistencia.objects.select_related(
        'matricula__estudiante', 
        'matricula__clase__curso',
        'clase'
    ).order_by('-fecha', 'matricula__estudiante__first_name')

    # Agrupar asistencias por clase y fecha
    historial_clases = {}
    for asistencia in asistencias:
        key = (asistencia.clase.id, asistencia.fecha)
        if key not in historial_clases:
            historial_clases[key] = {
                'clase': asistencia.clase,
                'curso': asistencia.curso,
                'fecha': asistencia.fecha,
                'profesor': asistencia.clase.profesor,
                'asistencias': []
            }
        historial_clases[key]['asistencias'].append(asistencia)

    # CAMBIO: Obtener todas las matrículas agrupadas por clase para el JavaScript
    # Esto es más simple que hacer una llamada API
    clases_con_estudiantes = Horario.objects.select_related('curso', 'profesor').annotate(
        total_estudiantes=models.Count('matriculas')
    ).filter(total_estudiantes__gt=0).order_by('-fecha_inicio', 'hora_inicio')

    # NUEVO: Preparar datos de estudiantes por clase para JavaScript
    # Crear un diccionario con todas las matrículas organizadas por clase
    estudiantes_por_clase = {}
    for clase in clases_con_estudiantes:
        matriculas = Matricula.objects.filter(clase=clase).select_related('estudiante')
        estudiantes_por_clase[str(clase.id)] = [
            {
                'id': matricula.estudiante.id,
                'nombre': matricula.estudiante.get_full_name(),
                'cedula': matricula.estudiante.cedula,
                'matricula_id': matricula.id,
            }
            for matricula in matriculas
        ]

    if request.method == 'POST':
        # Eliminar asistencia individual
        if request.POST.get('eliminar_asistencia') == '1':
            asistencia_id = request.POST.get('asistencia_id')
            try:
                asistencia = Asistencia.objects.get(id=asistencia_id)
                asistencia.delete()
                messages.success(request, 'Asistencia eliminada exitosamente.')
            except Asistencia.DoesNotExist:
                messages.error(request, 'Asistencia no encontrada.')
            return redirect('admin_asistencias')

        # Registrar asistencias masivas por clase
        elif request.POST.get('registrar_asistencias_clase') == '1':
            clase_id = request.POST.get('clase_id')
            fecha_str = request.POST.get('fecha_asistencia')
            
            try:
                clase = Horario.objects.get(id=clase_id)
                fecha_asistencia = datetime.strptime(fecha_str, '%Y-%m-%d').date()
                
                # Obtener todas las matrículas de esta clase
                matriculas_clase = Matricula.objects.filter(clase=clase).select_related('estudiante')
                
                if not matriculas_clase.exists():
                    messages.warning(request, 'No hay estudiantes matriculados en esta clase.')
                    return redirect('admin_asistencias')
                
                asistencias_creadas = 0
                asistencias_actualizadas = 0
                
                for matricula in matriculas_clase:
                    estudiante_id = str(matricula.estudiante.id)
                    estado = request.POST.get(f'estado_{estudiante_id}', EstadoAsistencia.AUSENTE)
                    observaciones = request.POST.get(f'observaciones_{estudiante_id}', '')
                    
                    # Verificar si ya existe asistencia para esta fecha y matrícula
                    asistencia_existente = Asistencia.objects.filter(
                        matricula=matricula, 
                        fecha=fecha_asistencia
                    ).first()
                    
                    if asistencia_existente:
                        # Actualizar asistencia existente
                        asistencia_existente.estado = estado
                        asistencia_existente.observaciones = observaciones
                        asistencia_existente.clase = clase
                        asistencia_existente.save()
                        asistencias_actualizadas += 1
                    else:
                        # Crear nueva asistencia
                        Asistencia.objects.create(
                            matricula=matricula,
                            clase=clase,
                            fecha=fecha_asistencia,
                            estado=estado,
                            observaciones=observaciones
                        )
                        asistencias_creadas += 1
                
                if asistencias_creadas > 0 and asistencias_actualizadas > 0:
                    messages.success(request, f'Asistencias procesadas: {asistencias_creadas} creadas, {asistencias_actualizadas} actualizadas.')
                elif asistencias_creadas > 0:
                    messages.success(request, f'{asistencias_creadas} asistencias registradas exitosamente.')
                elif asistencias_actualizadas > 0:
                    messages.success(request, f'{asistencias_actualizadas} asistencias actualizadas exitosamente.')
                else:
                    messages.info(request, 'No se procesaron asistencias.')
                
                return redirect('admin_asistencias')
                
            except (Horario.DoesNotExist, ValueError) as e:
                messages.error(request, 'Clase no encontrada o fecha inválida.')
                return redirect('admin_asistencias')

    # Filtros para la vista
    fecha_filtro = request.GET.get('fecha_filtro')
    clase_filtro = request.GET.get('clase_filtro')
    
    if fecha_filtro:
        try:
            fecha_obj = datetime.strptime(fecha_filtro, '%Y-%m-%d').date()
            asistencias = asistencias.filter(fecha=fecha_obj)
        except ValueError:
            pass
    
    if clase_filtro:
        try:
            asistencias = asistencias.filter(clase_id=clase_filtro)
        except ValueError:
            pass

    # Si hay filtro, filtra historial_clases
    if fecha_filtro or clase_filtro:
        historial_clases = {
            k: v for k, v in historial_clases.items()
            if (not fecha_filtro or str(v['fecha']) == fecha_filtro)
            and (not clase_filtro or str(v['clase'].id) == clase_filtro)
        }

    # NUEVO: Convertir historial_clases a formato JSON serializable
    historial_clases_json = {}
    for idx, (key, clase_info) in enumerate(historial_clases.items()):
        historial_clases_json[str(idx)] = {
            'clase': {
                'id': clase_info['clase'].id,
                'aula': clase_info['clase'].aula,
                'hora_inicio': str(clase_info['clase'].hora_inicio),
                'hora_fin': str(clase_info['clase'].hora_fin),
            },
            'curso': {
                'nombre': clase_info['curso'].nombre,
            },
            'fecha': str(clase_info['fecha']),
            'profesor': {
                'first_name': clase_info['profesor'].first_name,
                'last_name': clase_info['profesor'].last_name,
            },
            'asistencias': [
                {
                    'estudiante': {
                        'first_name': asistencia.estudiante.first_name,
                        'last_name': asistencia.estudiante.last_name,
                        'cedula': asistencia.estudiante.cedula,
                    },
                    'estado': asistencia.estado,
                    'observaciones': asistencia.observaciones or '',
                }
                for asistencia in clase_info['asistencias']
            ]
        }

    return render(request, 'usuarios/admin_asistencias.html', {
        'active_tab': 'asistencias',
        'historial_clases': historial_clases,
        'historial_clases_json': json.dumps(historial_clases_json),
        'clases': clases_con_estudiantes,
        'estudiantes_por_clase_json': json.dumps(estudiantes_por_clase),
        'estados_asistencia': EstadoAsistencia.choices,
        'fecha_hoy': date.today().strftime('%Y-%m-%d'),
        'fecha_filtro': fecha_filtro,
        'clase_filtro': clase_filtro,
    })

@login_required
@require_http_methods(["POST"])
def obtener_asistencias_fecha(request):
    """
    Función simple para obtener asistencias existentes de estudiantes en una fecha específica
    """
    if request.user.rol != Usuario.Rol.ADMIN:
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    try:
        data = json.loads(request.body)
        clase_id = data.get('clase_id')
        fecha_str = data.get('fecha')
        estudiante_ids = data.get('estudiante_ids', [])
        
        fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        
        # Buscar asistencias existentes para estos estudiantes en esta fecha
        asistencias_existentes = Asistencia.objects.filter(
            matricula__estudiante__id__in=estudiante_ids,
            fecha=fecha_obj
        ).select_related('matricula__estudiante')
        
        # Crear diccionario con estados de asistencia por estudiante
        resultado = {}
        for asistencia in asistencias_existentes:
            resultado[asistencia.matricula.estudiante.id] = {
                'estado': asistencia.estado,
                'observaciones': asistencia.observaciones or ''
            }
        
        return JsonResponse(resultado)
        
    except (ValueError, KeyError) as e:
        return JsonResponse({'error': 'Datos inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'Error interno del servidor'}, status=500)
    
    try:
        data = json.loads(request.body)
        clase_id = data.get('clase_id')
        fecha_str = data.get('fecha')
        estudiante_ids = data.get('estudiante_ids', [])
        
        fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        
        # Buscar asistencias existentes para estos estudiantes en esta fecha
        asistencias_existentes = Asistencia.objects.filter(
            matricula__estudiante__id__in=estudiante_ids,
            fecha=fecha_obj
        ).select_related('matricula__estudiante')
        
        # Crear diccionario con estados de asistencia por estudiante
        resultado = {}
        for asistencia in asistencias_existentes:
            resultado[asistencia.matricula.estudiante.id] = {
                'estado': asistencia.estado,
                'observaciones': asistencia.observaciones or ''
            }
        
        return JsonResponse(resultado)
        
    except (ValueError, KeyError) as e:
        return JsonResponse({'error': 'Datos inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'Error interno del servidor'}, status=500)

@login_required
def admin_reportes_redirect(request):
    """Redireccionar a la app de reportes"""
    return redirect('admin_reportes')
    return JsonResponse({'error': 'Error interno del servidor'}, status=500)

@login_required
def admin_reportes_redirect(request):
    """Redireccionar a la app de reportes"""
    return redirect('admin_reportes')
def admin_reportes_redirect(request):
    """Redireccionar a la app de reportes"""
    return redirect('admin_reportes')
