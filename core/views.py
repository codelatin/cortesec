from django.shortcuts import render
# Create your views here.
# core/views.py


def dashboard_view(request):
    """
    Vista principal del sistema.
    Muestra el panel de control con opciones para gestionar usuarios, roles y permisos.
    """
    context = {
        'page_title': 'Dashboard - Corte-Sec'
    }
    return render(request, 'core/dashboard.html', context)

def nosotros(request):
    return render(request, 'core/nosotros.html')

def caracteristicas(request):
    return render(request, 'core/caracteristicas.html')

def precios(request):
    return render(request, 'core/precios.html')

def contacto(request):
    return render(request, 'core/contacto.html')