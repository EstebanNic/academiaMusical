# home/views.py
from django.shortcuts import render

def index(request):
    return render(request, 'home/index.html')  # ruta de la plantilla
