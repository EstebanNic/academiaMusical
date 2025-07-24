from django.urls import path
from . import views

urlpatterns = [
    path('admin/', views.admin_reportes, name='admin_reportes'),
    path('pagos/pdf/', views.reporte_pagos_pdf, name='reporte_pagos_pdf'),
    path('asistencias/pdf/', views.reporte_asistencias_pdf, name='reporte_asistencias_pdf'),
    path('matriculas/pdf/', views.reporte_matriculas_pdf, name='reporte_matriculas_pdf'),
]
