from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('panel/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('panel/admin/profesores/', views.admin_profesores, name='admin_profesores'),
    path('panel/profesor/', views.profesor_dashboard, name='profesor_dashboard'),
    path('panel/estudiante/', views.estudiante_dashboard, name='estudiante_dashboard'),
    path('logout/', LogoutView.as_view(), name='logout'),

]
