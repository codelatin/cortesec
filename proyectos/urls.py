# proyectos/urls.py
from django.urls import path
from . import views

app_name = 'proyectos'  # ← este es el namespace que usarás en {% url %}

urlpatterns = [
    path('', views.project_list, name='project_list'),
    path('nuevo/', views.project_create, name='project_create'),
    path('<int:pk>/editar/', views.project_edit, name='project_edit'),
]