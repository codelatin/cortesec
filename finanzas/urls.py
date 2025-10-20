# finanzas/urls.py
from django.urls import path
from . import views

app_name = 'finanzas'

urlpatterns = [
    path('ingresos/', views.IngresoListView.as_view(), name='lista_ingresos'),
    path('ingresos/nuevo/', views.IngresoCreateView.as_view(), name='crear_ingreso'),
    path('ingresos/<int:pk>/editar/', views.IngresoUpdateView.as_view(), name='editar_ingreso'),
    path('ingresos/<int:pk>/recibir/', views.IngresoRecepcionView.as_view(), name='registrar_recepcion'),
]