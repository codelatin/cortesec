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
    return render(request, 'dashboard.html', context)