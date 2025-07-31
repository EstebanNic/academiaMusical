from django.urls import path
from . import views

urlpatterns = [
    path('panel/estudiantes/asistencias/', views.estudiante_asistencias, name='estudiante_asistencias'),
    path('panel/estudiantes/clases/', views.estudiante_clases, name='estudiante_clases'),
    path('panel/estudiantes/perfil/', views.estudiante_perfil, name='estudiante_perfil'),
]
