# core/urls.py
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('nosotros/', views.nosotros, name='nosotros'),
    path('caracteristicas/', views.caracteristicas, name='caracteristicas'),
    path('precios/', views.precios, name='precios'),
    path('contacto/', views.contacto, name='contacto'),
]