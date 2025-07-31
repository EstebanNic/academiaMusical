from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from horarios.models import Horario
from matriculas.models import Matricula
from pagos.models import Pago, EstadoPago
from asistencias.models import Asistencia, EstadoAsistencia
from datetime import date, timedelta
import json
from django.http import JsonResponse, HttpResponse
from usuarios.models import Usuario
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import get_template
from xhtml2pdf import pisa
import io

@login_required
def admin_profesores_dashboard(request):
    # Solo permite acceso a usuarios con rol PROFESOR
    if not hasattr(request.user, 'rol') or request.user.rol != 'PROFESOR':
        return render(request, 'profesores/acceso_denegado.html', status=403)
    # Redirigir directamente al panel de clases
    return redirect('profesor_clases')

@login_required
def profesor_clases(request):
    # Solo permite acceso a usuarios con rol PROFESOR
    if not hasattr(request.user, 'rol') or request.user.rol != 'PROFESOR':
        return render(request, 'profesores/acceso_denegado.html', status=403)
    clases = Horario.objects.filter(profesor=request.user).select_related('curso', 'aula').order_by('-fecha_inicio', '-hora_inicio')
    # Obtener estudiantes y estado de pago por clase
    estudiantes_por_clase = {}
    for clase in clases:
        matriculas = Matricula.objects.filter(clase=clase).select_related('estudiante')
        estudiantes_por_clase[clase.id] = [
            {
                'id': m.estudiante.id,
                'nombre': m.estudiante.get_full_name(),
                'cedula': m.estudiante.cedula,
                'matricula_id': m.id,
                'pagado': Pago.objects.filter(matricula=m, estado=EstadoPago.PAGADO).exists()
            }
            for m in matriculas
        ]
    return render(request, 'profesores/profesor_clases.html', {
        'clases': clases,
        'active_tab': 'clases',
        'estudiantes_por_clase_json': json.dumps(estudiantes_por_clase),
        'fecha_hoy': date.today().strftime('%Y-%m-%d'),
    })

@login_required
def profesor_asistencias(request):
    # Solo permite acceso a usuarios con rol PROFESOR
    if not hasattr(request.user, 'rol') or request.user.rol != 'PROFESOR':
        return render(request, 'profesores/acceso_denegado.html', status=403)
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    codigo_clase_filtro = request.GET.get('codigo_clase', '').upper()
    clases = Horario.objects.filter(profesor=request.user).select_related('curso', 'aula')
    asistencias = Asistencia.objects.filter(clase__profesor=request.user).select_related(
        'matricula__estudiante', 'clase', 'clase__curso'
    ).order_by('fecha', 'matricula__estudiante__first_name')
    fechas_rango = []
    if fecha_inicio and fecha_fin:
        asistencias = asistencias.filter(fecha__gte=fecha_inicio, fecha__lte=fecha_fin)
        try:
            inicio = date.fromisoformat(fecha_inicio)
            fin = date.fromisoformat(fecha_fin)
            delta = (fin - inicio).days
            fechas_rango = [(inicio + timedelta(days=i)) for i in range(delta + 1)]
        except Exception:
            fechas_rango = []
    elif fecha_inicio:
        asistencias = asistencias.filter(fecha=fecha_inicio)
        fechas_rango = [date.fromisoformat(fecha_inicio)]
    if codigo_clase_filtro:
        asistencias = [a for a in asistencias if a.clase.codigo.upper() == codigo_clase_filtro]

    # Agrupa asistencias por estudiante y fecha
    estudiantes_dict = {}
    asistencias_por_estudiante = {}
    for asistencia in asistencias:
        est_id = asistencia.matricula.estudiante.id
        estudiantes_dict[est_id] = asistencia.matricula.estudiante
        if est_id not in asistencias_por_estudiante:
            asistencias_por_estudiante[est_id] = {}
        asistencias_por_estudiante[est_id][asistencia.fecha] = asistencia

    tabla_asistencias = []
    for est_id, estudiante in estudiantes_dict.items():
        fila = {
            'estudiante': estudiante,
            'asistencias': []
        }
        for fecha in fechas_rango:
            asistencia = asistencias_por_estudiante.get(est_id, {}).get(fecha)
            fila['asistencias'].append(asistencia)
        # Agrega datos de clase solo una vez (todas son de la misma clase por filtro)
        fila['clase'] = asistencias[0].clase if asistencias else None
        tabla_asistencias.append(fila)

    return render(request, 'profesores/profesor_asistencias.html', {
        'active_tab': 'asistencias',
        'asistencias': asistencias,
        'clases': clases,
        'fecha_inicio': fecha_inicio or '',
        'fecha_fin': fecha_fin or '',
        'codigo_clase_filtro': codigo_clase_filtro,
        'fechas_rango': fechas_rango,
        'estudiantes_dict': estudiantes_dict,
        'asistencias_por_estudiante': asistencias_por_estudiante,
        'tabla_asistencias': tabla_asistencias,
    })

@csrf_exempt
@login_required
def guardar_asistencia_profesor(request):
    if request.method != 'POST' or not request.user.rol == 'PROFESOR':
        return JsonResponse({'success': False, 'error': 'No autorizado'}, status=403)
    try:
        data = json.loads(request.body)
        clase_id = data.get('clase_id')
        fecha = data.get('fecha')
        asistencias = data.get('asistencias', [])
        from horarios.models import Horario
        from matriculas.models import Matricula

        clase = Horario.objects.get(id=clase_id, profesor=request.user)
        fecha_obj = date.fromisoformat(fecha)
        for item in asistencias:
            estudiante_id = item.get('estudiante_id')
            estado = item.get('estado', EstadoAsistencia.AUSENTE)
            matricula = Matricula.objects.filter(clase=clase, estudiante_id=estudiante_id).first()
            if not matricula:
                continue
            asistencia_obj, created = Asistencia.objects.get_or_create(
                matricula=matricula,
                clase=clase,
                fecha=fecha_obj,
                defaults={'estado': estado}
            )
            if not created:
                asistencia_obj.estado = estado
                asistencia_obj.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@login_required
def profe_reportes_pdf(request):
    if not hasattr(request.user, 'rol') or request.user.rol != 'PROFESOR':
        return redirect('login')

    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    codigo_clase = request.GET.get('codigo_clase', '').upper()

    # Filtrar asistencias del profesor
    asistencias = Asistencia.objects.filter(
        clase__profesor=request.user
    ).select_related('matricula__estudiante', 'clase', 'clase__curso').order_by('fecha', 'matricula__estudiante__first_name')

    if fecha_inicio and fecha_fin:
        asistencias = asistencias.filter(fecha__gte=fecha_inicio, fecha__lte=fecha_fin)
    if codigo_clase:
        asistencias = [a for a in asistencias if a.clase.codigo.upper() == codigo_clase]

    # Obtener fechas del rango
    fechas_rango = []
    if fecha_inicio and fecha_fin:
        try:
            inicio = date.fromisoformat(fecha_inicio)
            fin = date.fromisoformat(fecha_fin)
            delta = (fin - inicio).days
            fechas_rango = [(inicio + timedelta(days=i)) for i in range(delta + 1)]
        except Exception:
            fechas_rango = []

    # Agrupa asistencias por estudiante y fecha
    estudiantes_dict = {}
    asistencias_por_estudiante = {}
    for asistencia in asistencias:
        est_id = asistencia.matricula.estudiante.id
        estudiantes_dict[est_id] = asistencia.matricula.estudiante
        if est_id not in asistencias_por_estudiante:
            asistencias_por_estudiante[est_id] = {}
        asistencias_por_estudiante[est_id][asistencia.fecha] = asistencia

    tabla_asistencias = []
    for est_id, estudiante in estudiantes_dict.items():
        fila = {
            'estudiante': estudiante,
            'asistencias': []
        }
        for fecha in fechas_rango:
            asistencia = asistencias_por_estudiante.get(est_id, {}).get(fecha)
            fila['asistencias'].append(asistencia)
        fila['clase'] = asistencias[0].clase if asistencias else None
        tabla_asistencias.append(fila)

    context = {
        'tabla_asistencias': tabla_asistencias,
        'fechas_rango': fechas_rango,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'codigo_clase': codigo_clase,
        'profesor': request.user,
        'fecha_generacion': date.today(),
    }

    template = get_template('profesores/profe_reportes.html')
    html = template.render(context)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        filename = f"reporte_asistencias_profesor_{date.today().strftime('%Y%m%d')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    return HttpResponse('Error al generar el PDF')
