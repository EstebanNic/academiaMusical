from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from asistencias.models import Asistencia
from datetime import date, timedelta

@login_required
def estudiante_asistencias(request):
    fecha_inicio = request.GET.get('fecha_inicio') or ''
    fecha_fin = request.GET.get('fecha_fin') or ''
    codigo_clase_filtro = request.GET.get('codigo_clase', '').upper()
    asistencias = []
    fechas_rango = []
    clase = None

    if fecha_inicio and fecha_fin and codigo_clase_filtro:
        asistencias_qs = Asistencia.objects.filter(
            matricula__estudiante=request.user
        ).select_related('clase__curso', 'matricula__clase')
        asistencias_qs = asistencias_qs.filter(fecha__gte=fecha_inicio, fecha__lte=fecha_fin)
        asistencias = [a for a in asistencias_qs if a.clase.codigo.upper() == codigo_clase_filtro]
        try:
            inicio = date.fromisoformat(fecha_inicio)
            fin = date.fromisoformat(fecha_fin)
            delta = (fin - inicio).days
            fechas_rango = [(inicio + timedelta(days=i)) for i in range(delta + 1)]
        except Exception:
            fechas_rango = []
        if asistencias:
            clase = asistencias[0].clase

    # Prepara la fila para la tabla
    fila_asistencias = []
    for fecha in fechas_rango:
        asistencia = next((a for a in asistencias if a.fecha == fecha), None)
        fila_asistencias.append(asistencia)

    return render(request, 'estudiantes/estudiante_asistencias.html', {
        'active_tab': 'asistencias',
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'codigo_clase_filtro': codigo_clase_filtro,
        'fechas_rango': fechas_rango,
        'fila_asistencias': fila_asistencias,
        'clase': clase,
        'estudiante': request.user,
    })

@login_required
def estudiante_clases(request):
    matriculas = request.user.matriculas.select_related('clase__curso', 'clase__aula', 'clase__profesor').all()
    return render(request, 'estudiantes/estudiante_clases.html', {
        'active_tab': 'clases',
        'matriculas': matriculas,
    })

@login_required
def estudiante_perfil(request):
    return render(request, 'estudiantes/estudiante_perfil.html', {
        'active_tab': 'perfil'
    })
