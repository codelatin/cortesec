# finanzas/views.py
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from .models import Ingreso
from .forms import IngresoForm, IngresoRecepcionForm, IngresoFilterForm
from proyectos.models import Project


class IngresoListView(LoginRequiredMixin, ListView):
    model = Ingreso
    template_name = 'finanzas/lista_ingresos.html'
    context_object_name = 'ingresos'
    paginate_by = 20  # opcional

    def get_queryset(self):
        # Solo ingresos de proyectos donde el usuario es miembro
        return Ingreso.objects.select_related('proyecto', 'creado_por').filter(
            proyecto__team_members__user=self.request.user,
            proyecto__team_members__is_active=True
        ).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filter_form = IngresoFilterForm(data=self.request.GET, user=self.request.user)
        context['filter_form'] = filter_form

        # Aplicar filtros al queryset
        if filter_form.is_valid():
            qs = context['ingresos']
            proyecto = filter_form.cleaned_data.get('proyecto')
            tipo_ingreso = filter_form.cleaned_data.get('tipo_ingreso')
            estado = filter_form.cleaned_data.get('estado')
            fecha_desde = filter_form.cleaned_data.get('fecha_desde')
            fecha_hasta = filter_form.cleaned_data.get('fecha_hasta')
            solo_vencidos = filter_form.cleaned_data.get('solo_vencidos')

            if proyecto:
                qs = qs.filter(proyecto=proyecto)
            if tipo_ingreso:
                qs = qs.filter(tipo_ingreso=tipo_ingreso)
            if estado:
                qs = qs.filter(estado=estado)
            if fecha_desde:
                qs = qs.filter(fecha_esperada__gte=fecha_desde)
            if fecha_hasta:
                qs = qs.filter(fecha_esperada__lte=fecha_hasta)
            if solo_vencidos:
                qs = qs.filter(esta_vencido=True)

            context['ingresos'] = qs

        return context


class IngresoCreateView(LoginRequiredMixin, CreateView):
    model = Ingreso
    form_class = IngresoForm
    template_name = 'finanzas/ingreso_form.html'
    success_url = reverse_lazy('finanzas:lista_ingresos')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.creado_por = self.request.user
        messages.success(self.request, 'Ingreso registrado exitosamente.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        print("❌ ERRORES DEL FORMULARIO:", form.errors)
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Registrar Nuevo Ingreso'
        context['submit_text'] = 'Agregar ingreso'
        return context
    


class IngresoUpdateView(LoginRequiredMixin, UpdateView):
    model = Ingreso
    form_class = IngresoForm
    template_name = 'finanzas/ingreso_form.html'
    success_url = reverse_lazy('finanzas:lista_ingresos')

    def get_queryset(self):
        # Solo permite editar ingresos de proyectos donde el usuario es miembro
        return Ingreso.objects.filter(
            proyecto__team_members__user=self.request.user,
            proyecto__team_members__is_active=True
        ).distinct()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Ingreso actualizado exitosamente.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Ingreso'
        context['submit_text'] = 'Actualizar ingreso'
        return context


class IngresoRecepcionView(LoginRequiredMixin, UpdateView):
    model = Ingreso
    form_class = IngresoRecepcionForm
    template_name = 'finanzas/ingreso_form.html'
    success_url = reverse_lazy('finanzas:lista_ingresos')

    def get_queryset(self):
        return Ingreso.objects.filter(
            proyecto__team_members__user=self.request.user,
            proyecto__team_members__is_active=True
        ).distinct()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Registrar Pago - {self.object.concepto}'
        context['submit_text'] = 'Registrar Pago'
        context['ingreso'] = self.object  # para el resumen lateral
        return context

    def form_valid(self, form):
        if self.object.estado == 'recibido':
            messages.warning(self.request, 'Este ingreso ya ha sido recibido completamente.')
            return redirect(self.success_url)
        messages.success(self.request, 'Pago registrado exitosamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Por favor corrige los errores del formulario.')
        return super().form_invalid(form)