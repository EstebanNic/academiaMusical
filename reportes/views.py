from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, FileResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from datetime import datetime, date
from pagos.models import Pago, EstadoPago
from matriculas.models import Matricula
from usuarios.models import Usuario
from cursos.models import Curso
from horarios.models import Horario
from django.db.models import Sum, Count, Min, Max, Q
import io

@login_required
def admin_reportes(request):
    if request.user.rol != Usuario.Rol.ADMIN:
        return redirect('login')
    
    # Obtener clases para el formulario de asistencias
    clases = Horario.objects.select_related('curso', 'profesor').all().order_by('curso__nombre', 'hora_inicio')
    cursos = Curso.objects.all().order_by('nombre')
    profesores = Usuario.objects.filter(rol=Usuario.Rol.PROFESOR).order_by('last_name', 'first_name')
    
    return render(request, 'usuarios/admin_reportes.html', {
        'active_tab': 'reportes',
        'clases': clases,
        'cursos': cursos,
        'profesores': profesores,
    })

@login_required
def reporte_pagos_pdf(request):
    if request.user.rol != Usuario.Rol.ADMIN:
        return redirect('login')
    
    # Obtener filtros de la URL
    fecha_inicio_str = request.GET.get('fecha_inicio')
    fecha_fin_str = request.GET.get('fecha_fin')
    estado_filtro = request.GET.get('estado')
    curso_id = request.GET.get('curso')
    clase_id = request.GET.get('clase')
    profesor_id = request.GET.get('profesor')
    q = request.GET.get('q')  # nombre o cédula del estudiante
    
    # Filtrar pagos
    pagos = Pago.objects.select_related(
        'matricula__estudiante', 
        'matricula__clase__curso'
    ).order_by('fecha_pago', 'matricula__estudiante__last_name', 'matricula__estudiante__first_name')
    
    # Parseo seguro de fechas (para mostrar correctamente en el template)
    def parse_date_param(value: str):
        if not value:
            return None
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except Exception:
            return None

    fecha_inicio = parse_date_param(fecha_inicio_str)
    fecha_fin = parse_date_param(fecha_fin_str)

    if fecha_inicio:
        pagos = pagos.filter(fecha_pago__gte=fecha_inicio)

    if fecha_fin:
        pagos = pagos.filter(fecha_pago__lte=fecha_fin)
    
    if estado_filtro:
        pagos = pagos.filter(estado=estado_filtro)
    if curso_id:
        pagos = pagos.filter(matricula__clase__curso_id=curso_id)
    if clase_id:
        pagos = pagos.filter(matricula__clase_id=clase_id)
    if profesor_id:
        pagos = pagos.filter(matricula__clase__profesor_id=profesor_id)
    if q:
        pagos = pagos.filter(
            Q(matricula__estudiante__first_name__icontains=q) |
            Q(matricula__estudiante__last_name__icontains=q) |
            Q(matricula__estudiante__cedula__icontains=q)
        )
    
    # Calcular totales
    total_pagos = pagos.aggregate(Sum('monto'))['monto__sum'] or 0
    total_pendientes = pagos.filter(estado=EstadoPago.PENDIENTE).aggregate(Sum('monto'))['monto__sum'] or 0
    total_pagados = pagos.filter(estado=EstadoPago.PAGADO).aggregate(Sum('monto'))['monto__sum'] or 0
    total_cancelados = pagos.filter(estado=EstadoPago.CANCELADO).aggregate(Sum('monto'))['monto__sum'] or 0
    
    # Estadísticas adicionales
    count_pendientes = pagos.filter(estado=EstadoPago.PENDIENTE).count()
    count_pagados = pagos.filter(estado=EstadoPago.PAGADO).count()
    count_cancelados = pagos.filter(estado=EstadoPago.CANCELADO).count()
    
    # Determinar período efectivo a mostrar
    periodo_inicio = fecha_inicio
    periodo_fin = fecha_fin
    if not periodo_inicio or not periodo_fin:
        # Si no vienen ambas fechas, tomar min/max del conjunto filtrado
        rangos = pagos.aggregate(min_fecha=Min('fecha_pago'), max_fecha=Max('fecha_pago'))
        periodo_inicio = periodo_inicio or rangos.get('min_fecha')
        periodo_fin = periodo_fin or rangos.get('max_fecha')

    # Obtener objetos seleccionados para mostrar en el PDF
    curso_sel = None
    clase_sel = None
    profesor_sel = None
    if curso_id:
        try:
            curso_sel = Curso.objects.get(id=curso_id)
        except Curso.DoesNotExist:
            curso_sel = None
    if clase_id:
        try:
            clase_sel = Horario.objects.select_related('curso').get(id=clase_id)
        except Horario.DoesNotExist:
            clase_sel = None
    if profesor_id:
        try:
            profesor_sel = Usuario.objects.get(id=profesor_id)
        except Usuario.DoesNotExist:
            profesor_sel = None

    # Contexto para el template
    context = {
        'pagos': pagos,
        'total_pagos': total_pagos,
        'total_pendientes': total_pendientes,
        'total_pagados': total_pagados,
        'total_cancelados': total_cancelados,
        'count_pendientes': count_pendientes,
        'count_pagados': count_pagados,
        'count_cancelados': count_cancelados,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'periodo_inicio': periodo_inicio,
        'periodo_fin': periodo_fin,
        'estado_filtro': estado_filtro,
        'curso_sel': curso_sel,
        'clase_sel': clase_sel,
        'profesor_sel': profesor_sel,
        'query_estudiante': q,
        'fecha_generacion': datetime.now(),
        'usuario_generador': request.user,
        'count_pagos': pagos.count(),
    }
    
    # Cargar template
    template = get_template('reportes/pagos_reporte_pdf.html')
    html = template.render(context)
    
    # Crear PDF
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result)
    
    if not pdf.err:
        # Enviar como inline para que el navegador lo abra en una nueva pestaña
        result.seek(0)
        return FileResponse(result, as_attachment=False, filename='reporte_pagos.pdf', content_type='application/pdf')
    
    return HttpResponse('Error al generar el PDF')

@login_required
def reporte_asistencias_pdf(request):
    if request.user.rol != Usuario.Rol.ADMIN:
        return redirect('login')
    
    # Obtener filtros de la URL
    fecha_inicio_str = request.GET.get('fecha_inicio')
    fecha_fin_str = request.GET.get('fecha_fin')
    clase_filtro = request.GET.get('clase')
    estado_filtro = request.GET.get('estado')
    curso_id = request.GET.get('curso')
    profesor_id = request.GET.get('profesor')
    q = request.GET.get('q')  # nombre o cédula del estudiante
    
    # Importar aquí para evitar dependencias circulares
    from asistencias.models import Asistencia, EstadoAsistencia
    from horarios.models import Horario
    from datetime import timedelta
    
    # Filtrar asistencias
    asistencias = Asistencia.objects.select_related(
        'matricula__estudiante',
        'matricula__clase__curso',
        'clase'
    ).order_by('fecha', 'matricula__estudiante__first_name')
    
    # Parseo seguro de fechas
    def parse_date_param(value: str):
        if not value:
            return None
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except Exception:
            return None

    fecha_inicio = parse_date_param(fecha_inicio_str)
    fecha_fin = parse_date_param(fecha_fin_str)

    if fecha_inicio:
        asistencias = asistencias.filter(fecha__gte=fecha_inicio)

    if fecha_fin:
        asistencias = asistencias.filter(fecha__lte=fecha_fin)
    
    if clase_filtro:
        asistencias = asistencias.filter(clase_id=clase_filtro)
    
    if estado_filtro:
        asistencias = asistencias.filter(estado=estado_filtro)

    if curso_id:
        asistencias = asistencias.filter(clase__curso_id=curso_id)

    if profesor_id:
        asistencias = asistencias.filter(clase__profesor_id=profesor_id)

    if q:
        asistencias = asistencias.filter(
            Q(matricula__estudiante__first_name__icontains=q) |
            Q(matricula__estudiante__last_name__icontains=q) |
            Q(matricula__estudiante__cedula__icontains=q)
        )
    
    # NUEVO: Generar estructura de datos para la tabla cruzada
    # 1. Obtener todas las fechas únicas en el rango
    fechas_unicas = sorted(set(asistencias.values_list('fecha', flat=True)))
    
    # 2. Obtener todos los estudiantes únicos
    estudiantes_unicos = {}
    for asistencia in asistencias:
        estudiante_id = asistencia.matricula.estudiante.id
        if estudiante_id not in estudiantes_unicos:
            estudiantes_unicos[estudiante_id] = {
                'estudiante': asistencia.matricula.estudiante,
                'curso': asistencia.matricula.clase.curso.nombre,
                'clase': asistencia.clase.aula,
                'asistencias_por_fecha': {},
                'present_count': 0,
                'tarde_count': 0,
                'asistio_count': 0,
            }
    
    # 3. Organizar asistencias por estudiante y fecha
    for asistencia in asistencias:
        estudiante_id = asistencia.matricula.estudiante.id
        fecha = asistencia.fecha
        estudiantes_unicos[estudiante_id]['asistencias_por_fecha'][fecha] = {
            'estado': asistencia.estado,
            'observaciones': asistencia.observaciones
        }
        # Contadores individuales por estudiante
        if asistencia.estado == EstadoAsistencia.PRESENTE:
            estudiantes_unicos[estudiante_id]['present_count'] += 1
            estudiantes_unicos[estudiante_id]['asistio_count'] += 1
        elif asistencia.estado == EstadoAsistencia.TARDE:
            estudiantes_unicos[estudiante_id]['tarde_count'] += 1
            estudiantes_unicos[estudiante_id]['asistio_count'] += 1
    
    # Calcular estadísticas generales
    total_asistencias = asistencias.count()
    total_presentes = asistencias.filter(estado=EstadoAsistencia.PRESENTE).count()
    total_tardanzas = asistencias.filter(estado=EstadoAsistencia.TARDE).count()
    total_ausentes = asistencias.filter(estado=EstadoAsistencia.AUSENTE).count()
    total_justificados = asistencias.filter(estado=EstadoAsistencia.JUSTIFICADO).count()
    
    # Porcentajes
    porcentaje_presentes = (total_presentes / total_asistencias * 100) if total_asistencias > 0 else 0
    porcentaje_ausentes = ((total_ausentes + total_tardanzas) / total_asistencias * 100) if total_asistencias > 0 else 0
    
    # Obtener información de la clase seleccionada
    clase_seleccionada = None
    if clase_filtro:
        try:
            clase_seleccionada = Horario.objects.select_related('curso', 'profesor').get(id=clase_filtro)
        except Horario.DoesNotExist:
            pass
    
    # Determinar período efectivo a mostrar
    periodo_inicio = fecha_inicio
    periodo_fin = fecha_fin
    if not periodo_inicio or not periodo_fin:
        rangos = asistencias.aggregate(min_fecha=Min('fecha'), max_fecha=Max('fecha'))
        periodo_inicio = periodo_inicio or rangos.get('min_fecha')
        periodo_fin = periodo_fin or rangos.get('max_fecha')

    # Obtener objetos seleccionados para mostrar en el PDF
    curso_sel = None
    profesor_sel = None
    if curso_id:
        try:
            curso_sel = Curso.objects.get(id=curso_id)
        except Curso.DoesNotExist:
            curso_sel = None
    if profesor_id:
        try:
            profesor_sel = Usuario.objects.get(id=profesor_id)
        except Usuario.DoesNotExist:
            profesor_sel = None

    # Contexto para el template
    context = {
        'estudiantes_data': estudiantes_unicos,
        'fechas_periodo': fechas_unicas,
        'total_asistencias': total_asistencias,
        'total_presentes': total_presentes,
        'total_tardanzas': total_tardanzas,
        'total_ausentes': total_ausentes,
        'total_justificados': total_justificados,
        'porcentaje_presentes': round(porcentaje_presentes, 1),
        'porcentaje_ausentes': round(porcentaje_ausentes, 1),
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'periodo_inicio': periodo_inicio,
        'periodo_fin': periodo_fin,
        'clase_filtro': clase_filtro,
        'clase_seleccionada': clase_seleccionada,
        'estado_filtro': estado_filtro,
        'curso_sel': curso_sel,
        'profesor_sel': profesor_sel,
        'query_estudiante': q,
        'fecha_generacion': datetime.now(),
        'usuario_generador': request.user,
        'total_estudiantes': len(estudiantes_unicos),
        'total_dias': len(fechas_unicas),
    }
    
    # Cargar template
    template = get_template('reportes/asistencias_reporte_pdf.html')
    html = template.render(context)
    
    # Crear PDF
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result)
    
    if not pdf.err:
        result.seek(0)
        return FileResponse(result, as_attachment=False, filename='reporte_asistencias.pdf', content_type='application/pdf')
    
    return HttpResponse('Error al generar el PDF')

@login_required
def reporte_matriculas_pdf(request):
    # Eliminado - no se usará por el momento
    return HttpResponse('Reporte no disponible')
