from django.urls import path
from . import views

urlpatterns = [
    path('panel/profesores/', views.admin_profesores_dashboard, name='admin_profesores_dashboard'),
    path('panel/profesores/clases/', views.profesor_clases, name='profesor_clases'),
    path('panel/profesores/asistencias/', views.profesor_asistencias, name='profesor_asistencias'),
    path('panel/profesores/cambiar-password/', views.profesor_cambiar_password, name='profesor_cambiar_password'),
    path('panel/profesores/perfil/', views.profesor_perfil, name='profesor_perfil'),
    path('panel/profesores/clases/guardar-asistencia/', views.guardar_asistencia_profesor, name='guardar_asistencia_profesor'),
    path('panel/profesores/asistencias/reporte-pdf/', views.profe_reportes_pdf, name='profe_reportes_pdf'),
]
