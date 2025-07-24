from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),  # usa de la vista personalizada
    path('panel/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('panel/admin/profesores/', views.admin_profesores, name='admin_profesores'),
    path('panel/admin/estudiantes/', views.admin_estudiantes, name='admin_estudiantes'),
    path('panel/admin/cursos/', views.admin_cursos, name='admin_cursos'),
    path('panel/admin/clases/', views.admin_clases, name='admin_clases'),
    path('panel/admin/matriculas/', views.admin_matriculas, name='admin_matriculas'),
    path('panel/admin/pagos/', views.admin_pagos, name='admin_pagos'),
    path('panel/admin/asistencias/', views.admin_asistencias, name='admin_asistencias'),
    path('panel/admin/asistencias/estudiantes-fecha/', views.obtener_asistencias_fecha, name='obtener_asistencias_fecha'),
    path('panel/profesor/', views.profesor_dashboard, name='profesor_dashboard'),
    path('panel/estudiante/', views.estudiante_dashboard, name='estudiante_dashboard'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('panel/admin/reportes/', views.admin_reportes_redirect, name='admin_reportes_redirect'),
]

