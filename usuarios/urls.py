from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),  # usa tu vista personalizada
    path('panel/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('panel/admin/profesores/', views.admin_profesores, name='admin_profesores'),
    path('panel/admin/estudiantes/', views.admin_estudiantes, name='admin_estudiantes'),
    path('panel/admin/cursos/', views.admin_cursos, name='admin_cursos'),
    path('panel/profesor/', views.profesor_dashboard, name='profesor_dashboard'),
    path('panel/estudiante/', views.estudiante_dashboard, name='estudiante_dashboard'),
    path('logout/', LogoutView.as_view(), name='logout'),

]
