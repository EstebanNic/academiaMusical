from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from datetime import datetime, date
from pagos.models import Pago, EstadoPago
from matriculas.models import Matricula
from usuarios.models import Usuario
from django.db.models import Sum, Count
import io

@login_required
def admin_reportes(request):
    if request.user.rol != Usuario.Rol.ADMIN:
        return redirect('login')
    
    # Obtener clases para el formulario de asistencias
    from horarios.models import Horario
    clases = Horario.objects.select_related('curso', 'profesor').all().order_by('curso__nombre', 'hora_inicio')
    
    return render(request, 'usuarios/admin_reportes.html', {
        'active_tab': 'reportes',
        'clases': clases
    })

@login_required
def reporte_pagos_pdf(request):
    if request.user.rol != Usuario.Rol.ADMIN:
        return redirect('login')
    
    # Obtener filtros de la URL
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    estado_filtro = request.GET.get('estado')
    
    # Filtrar pagos
    pagos = Pago.objects.select_related(
        'matricula__estudiante', 
        'matricula__clase__curso'
    ).order_by('-fecha_pago')
    
    if fecha_inicio:
        pagos = pagos.filter(fecha_pago__gte=fecha_inicio)
    
    if fecha_fin:
        pagos = pagos.filter(fecha_pago__lte=fecha_fin)
    
    if estado_filtro:
        pagos = pagos.filter(estado=estado_filtro)
    
    # Calcular totales
    total_pagos = pagos.aggregate(Sum('monto'))['monto__sum'] or 0
    total_pendientes = pagos.filter(estado=EstadoPago.PENDIENTE).aggregate(Sum('monto'))['monto__sum'] or 0
    total_pagados = pagos.filter(estado=EstadoPago.PAGADO).aggregate(Sum('monto'))['monto__sum'] or 0
    total_cancelados = pagos.filter(estado=EstadoPago.CANCELADO).aggregate(Sum('monto'))['monto__sum'] or 0
    
    # Estadísticas adicionales
    count_pendientes = pagos.filter(estado=EstadoPago.PENDIENTE).count()
    count_pagados = pagos.filter(estado=EstadoPago.PAGADO).count()
    count_cancelados = pagos.filter(estado=EstadoPago.CANCELADO).count()
    
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
        'estado_filtro': estado_filtro,
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
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        filename = f"reporte_pagos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    
    return HttpResponse('Error al generar el PDF')

@login_required
def reporte_asistencias_pdf(request):
    if request.user.rol != Usuario.Rol.ADMIN:
        return redirect('login')
    
    # Obtener filtros de la URL
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    clase_filtro = request.GET.get('clase')
    estado_filtro = request.GET.get('estado')
    
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
    
    if fecha_inicio:
        asistencias = asistencias.filter(fecha__gte=fecha_inicio)
    
    if fecha_fin:
        asistencias = asistencias.filter(fecha__lte=fecha_fin)
    
    if clase_filtro:
        asistencias = asistencias.filter(clase_id=clase_filtro)
    
    if estado_filtro:
        asistencias = asistencias.filter(estado=estado_filtro)
    
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
                'asistencias_por_fecha': {}
            }
    
    # 3. Organizar asistencias por estudiante y fecha
    for asistencia in asistencias:
        estudiante_id = asistencia.matricula.estudiante.id
        fecha = asistencia.fecha
        estudiantes_unicos[estudiante_id]['asistencias_por_fecha'][fecha] = {
            'estado': asistencia.estado,
            'observaciones': asistencia.observaciones
        }
    
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
        'clase_filtro': clase_filtro,
        'clase_seleccionada': clase_seleccionada,
        'estado_filtro': estado_filtro,
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
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        filename = f"reporte_asistencias_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    
    return HttpResponse('Error al generar el PDF')

@login_required
def reporte_matriculas_pdf(request):
    # Eliminado - no se usará por el momento
    return HttpResponse('Reporte no disponible')
