# proyectos/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Project
from .forms import ProjectForm

@login_required
def project_list(request):
    """
    Muestra la lista de proyectos creados por el usuario autenticado.
    Si el usuario es staff o superusuario, ve todos los proyectos.
    """
    if request.user.is_staff or request.user.is_superuser:
        projects = Project.objects.all().order_by('-created_at')
    else:
        projects = Project.objects.filter(created_by=request.user).order_by('-created_at')

    return render(request, 'proyectos/project_list.html', {
        'object_list': projects,
    })


@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, current_user=request.user)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()
            messages.success(request, f'Obra "{project.name}" creada exitosamente.')
            return redirect('proyectos:project_list')
    else:
        form = ProjectForm(current_user=request.user)
    
    return render(request, 'proyectos/project_form.html', {
        'form': form,
        'title': 'Crear Nueva Obra'
    })


@login_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk, created_by=request.user)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project, current_user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Obra "{project.name}" actualizada exitosamente.')
            return redirect('proyectos:project_list')
    else:
        form = ProjectForm(instance=project, current_user=request.user)
    
    return render(request, 'proyectos/project_form.html', {
        'form': form,
        'title': 'Editar Obra',
        'project': project
    })
