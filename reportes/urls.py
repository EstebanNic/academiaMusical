from django.urls import path
from . import views
from usuarios import views as usuarios_views  # Importa la vista desde usuarios

urlpatterns = [
    path('admin/', views.admin_reportes, name='admin_reportes'),
    path('pagos/pdf/', views.reporte_pagos_pdf, name='reporte_pagos_pdf'),
    path('asistencias/pdf/', views.reporte_asistencias_pdf, name='reporte_asistencias_pdf'),
    path('matriculas/pdf/', views.reporte_matriculas_pdf, name='reporte_matriculas_pdf'),
    # --- NUEVA RUTA PARA FACTURA PDF ---
    path('factura_pago/<int:pago_id>/', usuarios_views.factura_pago_pdf, name='factura_pago_pdf'),
]
